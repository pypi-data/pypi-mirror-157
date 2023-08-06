# -*- coding: utf-8 -*-

"""
https://stackoverflow.com/questions/71443139/shacl-sparqltarget-not-validating-the-sparql-query-output-nodes
"""

import rdflib

from pyshacl import validate


shacl_file = r'''
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix snomed: <http://localhost:8890/snomed/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

snomed:
    sh:declare [
        sh:prefix "snomed" ;
        sh:namespace "http://localhost:8890/snomed/"^^xsd:anyURI ;
    ] .

snomed:dob363698007Shape
    a sh:NodeShape ;
    sh:target [
        a sh:SPARQLTarget ;
        sh:prefixes snomed: ;
        sh:select "SELECT ?this WHERE { ?node a snomed:24078009.?node a snomed:dob .?node snomed:609096000 ?this.?this a  snomed:dob363698007 .bind(?node as ?conceptName).bind(?this as ?RGName) .FILTER(REGEX(strafter(xsd:string(?RGName),'snomed/'),strafter(xsd:string(?conceptName),'snomed/')) ).}";
        ] ;
    sh:property [
        sh:path snomed:363698007;
        sh:minCount 1;
    ].
'''


data_file = '''
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix snomed: <http://localhost:8890/snomed/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
snomed:dob a rdfs:Class,snomed:dob ;
       rdfs:label "Semantic Pattern dob"^^xsd:string ;
        snomed:609096000 snomed:dob363698007 .

    snomed:dob363698007 a rdfs:Class,snomed:dob363698007;
       snomed:363698007 snomed:123037004 .


    snomed:24078009 a rdfs:Class, snomed:24078009, snomed:dob;
        rdfs:label "Gangosa of yaws (disorder)"^^xsd:string ;
        snomed:609096000 snomed:24078009_3,snomed:24078009_5,snomed:24078009_6;
        rdfs:subClassOf snomed:128349005,
            snomed:140004,
            snomed:177010002,
            snomed:312118003,
            snomed:312129004,
            snomed:312422001,
            snomed:363166002,
            snomed:47841006,
            snomed:88037009 .

    snomed:24078009_3 a rdfs:Class, snomed:24078009_3, snomed:dob363698007 ;
        snomed:263502005 snomed:90734009 .

    snomed:24078009_5 a rdfs:Class, snomed:24078009_5,snomed:dob363698007;
        snomed:116676008 snomed:110435003 ;
        snomed:246075003 snomed:6246005 ;
        snomed:363698007 snomed:71836000 ;
        snomed:370135005 snomed:441862004 .

    snomed:24078009_6 a rdfs:Class, snomed:24078009_6,snomed:dob363698007 ;
        snomed:116676008 snomed:110435003 ;
        snomed:246075003 snomed:6246005 ;
        snomed:363698007 snomed:72914001 ;
        snomed:370135005 snomed:441862004 .
'''


def test_stackoverflow_1() -> None:
    data = rdflib.Graph()
    data.parse(data=data_file, format="turtle")
    shapes = rdflib.Graph()
    shapes.parse(data=shacl_file, format="turtle")
    res = validate(
        data, shacl_graph=shapes, data_graph_format='turtle', shacl_graph_format='turtle', debug=True, advanced=True
    )
    conforms, graph, string = res
    assert False == conforms


if __name__ == "__main__":
    test_stackoverflow_1()
