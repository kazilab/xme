from xme_phases.builder import build_xme_list


def test_build_from_small_hgnc_fixture(tmp_path):
    fixture = tmp_path / "hgnc_complete_set.txt"
    fixture.write_text(
        "hgnc_id\tsymbol\tname\tstatus\tentrez_id\tensembl_gene_id\tuniprot_ids\tlocation\tgene_group\tgene_group_id\n"
        "HGNC:2597\tCYP1A1\tcytochrome P450 family 1 subfamily A member 1\tApproved\t1543\tENSG00000140465\tP04798\t15q24.1\tCytochrome P450 family 1\t123\n"
        "HGNC:4632\tGSTM1\tglutathione S-transferase mu 1\tApproved\t2944\tENSG00000134184\tP09488\t1p13.3\tGlutathione S-transferases\t456\n"
        "HGNC:40\tABCB1\tATP binding cassette subfamily B member 1\tApproved\t5243\tENSG00000085563\tP08183\t7q21.12\tATP binding cassette transporters\t789\n"
        "HGNC:6833\tMAOA\tmonoamine oxidase A\tApproved\t4128\tENSG00000189221\tP21397\tXp11.3\t\t\n"
        "HGNC:6928\tGLYAT\tglycine-N-acyltransferase\tApproved\t10249\tENSG00000149124\tQ6IB77\t11q12.1\t\t\n"
        "HGNC:932\tBAAT\tbile acid-CoA:amino acid N-acyltransferase\tApproved\t570\tENSG00000136881\tQ14032\t9q31.1\t\t\n"
        "HGNC:999\tNOTXME\tnot an xme\tApproved\t\t\t\t1q1\t\t\n",
        encoding="utf-8",
    )
    records = build_xme_list(hgnc_tsv_path=fixture)
    symbols = {r.symbol for r in records}
    assert {"CYP1A1", "GSTM1", "ABCB1", "MAOA", "GLYAT", "BAAT"}.issubset(symbols)
    assert "NOTXME" not in symbols
