# Verbinden met AAT 

Om verbindingen met AAT termen te kunnen leggen zijn op [https://triplydb.com/getty/aat/sparql/aat](https://triplydb.com/getty/aat/sparql/aat) in vier keer (hoog de `offset` steeds met 10000 op) alle 37.039 Nederlandse preflabels opgehaald met de volgende query:

```
PREFIX dataset: <http://vocab.getty.edu/dataset/>
PREFIX void: <http://rdfs.org/ns/void#>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX skos-xl: <http://www.w3.org/2008/05/skos-xl#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX vocab: <http://vocab.getty.edu/ontology#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT * WHERE {
  ?term void:inDataset dataset:aat .
  ?term skos-xl:prefLabel ?nllabel .
  ?nllabel dct:language <http://vocab.getty.edu/language/nl> .
  ?nllabel skos-xl:literalForm ?preflabel .
}
offset 0 limit 10000
```

Daarna zijn ook de 26.159 altlabels opgehaald (in drie keer), door in de query `skos-xl:prefLabel` te vervangen door `skos-xl:altLabel`.

Alternatief had ik de endpoint per term kunnen aanroepen, met een query als hieronder, maar dan had ik de endpoint 1591 ipv 7 keer moeten aanroepen (zoveel trefwoorden gebruikte De Boer).

```
PREFIX skos-xl: <http://www.w3.org/2008/05/skos-xl#>
SELECT ?term ?preforalt ?label WHERE {
  ?nllabel skos-xl:literalForm ?label .
  ?term ?preforalt ?nllabel .
  FILTER(?label = "gemeenteraad"@nl)
}
```
