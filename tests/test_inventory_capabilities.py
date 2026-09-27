"""Inventory -> operation selection -> real build, using the existing fixture."""
from pathlib import Path
import copy,importlib.util,json,sys,tempfile,unittest
from lxml import etree as E

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import review_docx as review
spec=importlib.util.spec_from_file_location('inventory_fixture',ROOT/'examples/complex-word/build_fixture.py')
fixture=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture)


class InventoryCapabilities(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.dir=Path(self.temp.name)
        self.doc,self.plan=fixture.build(self.dir/'source')
        self.infos,self.parts,self.root=review.read_package(self.doc)

    def tearDown(self):self.temp.cleanup()

    def save_variant(self,root,name):
        path=self.dir/(name+'.docx');review.write_package(path,self.infos,self.parts,root)
        return path

    def test_legacy_editable_and_executable_routes_are_distinct(self):
        inv=review.inventory(self.doc)
        for p,row in zip(review.paragraphs(self.root),inv['paragraphs']):
            self.assertEqual(row['editable'],review.plain_reason(p) is None)
            self.assertEqual(row['reason'],review.plain_reason(p))
        plain,complex_row=inv['paragraphs'][0],inv['paragraphs'][2]
        self.assertTrue(plain['editable']);self.assertFalse(plain['whole_paragraph']['available'])
        self.assertFalse(complex_row['editable']);self.assertTrue(complex_row['ordinary_spans']['available'])
        self.assertEqual(complex_row['recommended_route'],'replace_span')
        self.assertEqual(complex_row['operations'],['replace_span'])
        self.assertEqual(inv['document_blockers'][0]['code'],'existing_tracked_revisions')
        self.assertTrue(inv['document_blockers'][0]['locations'])
        values=[g['text'] for g in complex_row['ordinary_spans']['groups']]
        for value in ['T = R × P','Table 1','the model note','Measurement pending.',' Prior insertion.']:
            self.assertNotIn(value,values)
        self.assertIn('T',values)  # Styling alone is not a blanket span refusal.
        protected=complex_row['protected_content']
        self.assertTrue(any(x['text']=='Table 1' and 'cached result' in x['reason'] for x in protected))
        self.assertTrue(all(x['location'] for x in protected))
        self.assertTrue(inv['unsupported_operations']);self.assertTrue(inv['plan_selection'])

    def test_inventory_selected_spans_build_both_artifacts_and_preserve_content(self):
        inv=review.inventory(self.doc);plan=copy.deepcopy(self.plan);ops=[]
        # Select actual advertised operations; also route an ordinary paragraph
        # through the same span plan instead of making an invalid mixed plan.
        for pid,after in [('P0002','Illustrative arithmetic example. It is not a physical experiment.'),
                          ('P0003',self.plan['operations'][0]['spans'][0]['after']+' ')]:
            row=next(p for p in inv['paragraphs'] if p['id']==pid)
            group=next(g for g in row['ordinary_spans']['groups'] if g['replaceable_as_whole_group'])
            selected=group['operation']
            self.assertEqual(len(group['run_locations']),group['run_count'])
            ops.append({'id':'C'+str(len(ops)+1),'kind':selected['kind'],'target':selected['target'],
                        'expect':row['text'],'spans':[{'before':selected['before'],'after':after}],
                        'purpose':'Inventory-selected local wording correction',
                        'evidence':'Existing complex-word arithmetic teaching fixture','confirm':False})
        plan.update(input_sha256=inv['sha256'],operations=ops)
        manifest=self.dir/'selected.json';manifest.write_text(json.dumps(plan),encoding='utf8')
        output=self.dir/'built';payload=review.build(self.doc,manifest,output,True)
        self.assertEqual(payload['checks']['status'],'PASS')
        self.assertEqual(len(payload['changes']),2)
        old_highlights=[review.canonical(x) for x in self.root.xpath('//w:r[w:rPr/w:highlight]',namespaces=review.NS)]
        queries=['//m:oMath','//w:r[w:rPr/w:i]','//w:hyperlink','//w:tbl','//w:fldChar','//w:instrText']
        for name,highlight in [('input_包装审阅版.docx',True),('input_清洁候选稿.docx',False)]:
            target=output/name;revised=review.read_package(target)[2]
            self.assertEqual(review.verify_pair(self.doc,target)['status'],'PASS')
            self.assertEqual(review.SPAN.protected_history(self.root),review.SPAN.protected_history(revised))
            self.assertEqual(review.SPAN.field_runs(self.root)[1],review.SPAN.field_runs(revised)[1])
            for query in queries:
                self.assertEqual([review.canonical(x) for x in self.root.xpath(query,namespaces=review.NS)],
                                 [review.canonical(x) for x in revised.xpath(query,namespaces=review.NS)])
            current=[review.canonical(x) for x in revised.xpath('//w:r[w:rPr/w:highlight]',namespaces=review.NS)]
            for value in old_highlights:self.assertIn(value,current)
            yellow=revised.xpath('//w:r[w:rPr/w:highlight[@w:val="yellow"]]',namespaces=review.NS)
            self.assertEqual([review.text(r) for r in yellow],[op['spans'][0]['after'] for op in ops] if highlight else [])
            for op in ops:self.assertIn(op['spans'][0]['after'],review.text(revised))

    def test_field_selection_still_refuses_without_publishing_or_mutating_source(self):
        original=self.doc.read_bytes();plan=copy.deepcopy(self.plan)
        plan['operations'][0]['spans']=[{'before':'Table 1','after':'Table 2'}]
        manifest=self.dir/'field.json';manifest.write_text(json.dumps(plan),encoding='utf8')
        with self.assertRaisesRegex(ValueError,'0 eligible matches'):
            review.build(self.doc,manifest,self.dir/'refused',True)
        self.assertEqual(self.doc.read_bytes(),original);self.assertFalse((self.dir/'refused').exists())
        self.assertEqual(review.SPAN.field_runs(self.root)[1],review.SPAN.field_runs(review.read_package(self.doc)[2])[1])

    def test_contiguous_same_style_runs_are_one_located_group(self):
        root=copy.deepcopy(self.root);p=review.paragraphs(root)[2];run=p[0]
        run.find('w:t',review.NS).text='The design ';tail=copy.deepcopy(run)
        tail.find('w:t',review.NS).text='proves better cooling. ';p.insert(1,tail)
        inv=review.inventory(self.save_variant(root,'split'));g=inv['paragraphs'][2]['ordinary_spans']['groups'][0]
        self.assertEqual(g['run_count'],2);self.assertEqual(g['paragraph_child_indices'],[1,2])
        self.assertEqual(g['operation']['before'],'The design proves better cooling. ')
        self.assertNotEqual(g['format_sha256'],inv['paragraphs'][2]['ordinary_spans']['groups'][1]['format_sha256'])
        plan=copy.deepcopy(self.plan);plan['operations'][0]['spans'][0]['before']=g['operation']['before']
        revised,_=review.apply_plan(root,plan,False)
        self.assertIn(plan['operations'][0]['spans'][0]['after'],review.text(revised))

    def test_ambiguous_group_is_located_but_not_advertised_as_executable(self):
        root=copy.deepcopy(self.root);p=review.paragraphs(root)[2]
        p[0].find('w:t',review.NS).text='T'  # Same text as the adjacent italic group.
        inv=review.inventory(self.save_variant(root,'ambiguous'));groups=inv['paragraphs'][2]['ordinary_spans']['groups']
        for group in groups[:2]:
            self.assertTrue(group['eligible']);self.assertFalse(group['replaceable_as_whole_group'])
            self.assertEqual(group['eligible_match_count'],2);self.assertIsNone(group['operation'])
        plan=copy.deepcopy(self.plan);plan['operations'][0]['expect']=review.text(p)
        plan['operations'][0]['spans']=[{'before':'T','after':'U'}]
        with self.assertRaisesRegex(ValueError,'2 eligible matches'):review.apply_plan(root,plan,False)

    def test_no_history_restores_whole_route_but_mixed_plan_remains_unsupported(self):
        root=copy.deepcopy(self.root)
        for node in root.xpath('//w:ins | //w:del',namespaces=review.NS):node.getparent().remove(node)
        inv=review.inventory(self.save_variant(root,'no-history'))
        row=inv['paragraphs'][0];self.assertTrue(row['whole_paragraph']['available'])
        whole={'id':'C2','kind':row['recommended_route'],'target':row['id'],'expect':row['text'],
               'text':row['text']+' (review)','purpose':'Fixture title','evidence':'Fixture','confirm':False}
        revised,_=review.apply_plan(root,{'operations':[whole]},False)
        self.assertIn('(review)',review.text(revised))
        plan=copy.deepcopy(self.plan);plan['operations'][0]['expect']=inv['paragraphs'][2]['text']
        plan['operations'].append(whole)
        with self.assertRaisesRegex(ValueError,'do not combine paragraph replacement'):review.apply_plan(root,plan,False)

    def test_plain_looking_cross_paragraph_field_cache_has_no_edit_route(self):
        root=copy.deepcopy(self.root)
        for node in root.xpath('//w:ins | //w:del',namespaces=review.NS):node.getparent().remove(node)
        p=review.paragraphs(root)[2];end=root.xpath('//w:fldChar[@w:fldCharType="end"]',namespaces=review.NS)[0].getparent()
        result=root.xpath('//w:r[w:t="Table 1"]',namespaces=review.NS)[0]
        p.remove(result);p.remove(end);cache=E.Element(review.Q('p'));cache.append(result)
        close=E.Element(review.Q('p'));close.append(end);p.addnext(cache);cache.addnext(close)
        inv=review.inventory(self.save_variant(root,'cross-paragraph-field'));row=inv['paragraphs'][3]
        self.assertEqual(row['text'],'Table 1');self.assertTrue(row['editable'])
        self.assertFalse(row['operations']);self.assertIsNone(row['recommended_route'])
        self.assertIn('cached result',row['whole_paragraph']['blocked_by'][0])
        whole={'id':'C1','kind':'replace','target':row['id'],'expect':row['text'],'text':'Table 2',
               'purpose':'Rejected cache edit','evidence':'Fixture','confirm':False}
        with self.assertRaisesRegex(ValueError,'cached result'):review.apply_plan(root,{'operations':[whole]},False)

    def test_section_boundary_disables_otherwise_eligible_span(self):
        root=copy.deepcopy(self.root);p=review.paragraphs(root)[1]
        pp=E.Element(review.Q('pPr'));pp.append(copy.deepcopy(root.find('w:body/w:sectPr',review.NS)));p.insert(0,pp)
        inv=review.inventory(self.save_variant(root,'section-boundary'));row=inv['paragraphs'][1]
        self.assertTrue(row['ordinary_spans']['groups'][0]['eligible'])
        self.assertFalse(row['operations']);self.assertIsNone(row['recommended_route'])
        self.assertIn('section boundary',row['ordinary_spans']['blocked_by'][0])
        plan=copy.deepcopy(self.plan);op=plan['operations'][0]
        op.update(target=row['id'],expect=row['text'],spans=[{'before':row['text'],'after':'Changed text'}])
        with self.assertRaisesRegex(ValueError,'section boundary'):review.apply_plan(root,plan,False)

    def test_malformed_fields_are_located_and_block_inspect_and_build_routes(self):
        for mutation in ['unclosed','unknown','missing_type','unmatched_end','unmatched_separator','duplicate_separator','orphan_instruction','instruction_after_result']:
            with self.subTest(mutation=mutation):
                root=copy.deepcopy(self.root);chars=root.xpath('//w:fldChar',namespaces=review.NS)
                if mutation=='unclosed':chars[-1].getparent().remove(chars[-1])
                elif mutation=='unknown':chars[0].set(review.Q('fldCharType'),'invalid')
                elif mutation=='missing_type':del chars[0].attrib[review.Q('fldCharType')]
                elif mutation=='unmatched_end':chars[0].set(review.Q('fldCharType'),'end')
                elif mutation=='unmatched_separator':chars[0].set(review.Q('fldCharType'),'separate')
                elif mutation=='duplicate_separator':chars[-1].set(review.Q('fldCharType'),'separate')
                elif mutation=='orphan_instruction':chars[0].getparent().remove(chars[0])
                else:
                    instruction=root.xpath('//w:instrText',namespaces=review.NS)[0].getparent()
                    chars[1].getparent().addnext(instruction)
                doc=self.save_variant(root,mutation);original=doc.read_bytes();inv=review.inventory(doc)
                self.assertEqual(inv['field_structure']['status'],'BLOCKED')
                self.assertTrue(inv['document_blockers'][0]['locations'][0].startswith('/'))
                for row in inv['paragraphs']:
                    self.assertFalse(row['operations']);self.assertIsNone(row['recommended_route'])
                    self.assertFalse(row['ordinary_spans']['groups'])
                plan=copy.deepcopy(self.plan);plan['input_sha256']=inv['sha256']
                manifest=self.dir/(mutation+'.json');manifest.write_text(json.dumps(plan),encoding='utf8')
                with self.assertRaisesRegex(ValueError,'no edits applied'):
                    review.build(doc,manifest,self.dir/(mutation+'-output'),True)
                self.assertEqual(doc.read_bytes(),original);self.assertFalse((self.dir/(mutation+'-output')).exists())


if __name__=='__main__':unittest.main()
