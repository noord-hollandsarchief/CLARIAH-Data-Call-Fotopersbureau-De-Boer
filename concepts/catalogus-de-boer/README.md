# Verbinden met AAT 

De Art & Architecture Thesaurus (AAT), is een thesaurus voor cultuur- en erfgoedterminologie van het Amerikaanse Getty Center. Deze thesaurus wordt wereldwijd toegepast voor het toegankelijk maken van cultureel erfgoed: niet alleen voor kunst- en architectuurcollecties, maar ook voor collecties op het gebied van kunstnijverheid, archeologie, archiefmaterialen en materiële cultuur. (tekst van [Wikipedia](https://nl.wikipedia.org/wiki/Art_%26_Architecture_Thesaurus#Andere_gecontroleerde_terminologiebronnen)).

- [AAT 'homepage'](https://www.getty.edu/research/tools/vocabularies/aat/index.html)
- [AAT hiërarchie](https://www.getty.edu/vow/AATHierarchy?find=&logic=AND&note=&subjectid=300000000)
- [AAT 'semantic view'](http://vocab.getty.edu/aat/)
 
## Automatisch verbindingen leggen

Om verbindingen met AAT termen te kunnen leggen zijn op [https://triplydb.com/getty/aat/sparql/aat](https://triplydb.com/getty/aat/sparql/aat) in vier keer (hoog de `offset` steeds met 10000 op) alle 37.039 Nederlandse preflabels opgehaald met de volgende query:

```SPARQL
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

Daarna zijn ook de 26.159 altlabels opgehaald (in drie keer), door in de query `skos-xl:prefLabel` te vervangen door `skos-xl:altLabel`. Ik vond het wel leuk om te weten dat er dus 

Alle 63.198 labels heb ik in een database opgenomen en daar heb ik de trefwoorden van De Boer tegenaan gehouden.

Alternatief had ik de endpoint per term kunnen aanroepen, met een query als hieronder, maar dan had ik de endpoint 1591 ipv 7 keer moeten aanroepen (zoveel trefwoorden gebruikte De Boer).

```SPARQL
PREFIX skos-xl: <http://www.w3.org/2008/05/skos-xl#>
SELECT ?term ?preforalt ?label WHERE {
  ?nllabel skos-xl:literalForm ?label .
  ?term ?preforalt ?nllabel .
  FILTER(?label = "gemeenteraad"@nl)
}
```

## Aantal verbonden termen

Daarna zijn veel relaties nog handmatig gelegd. In totaal zijn er nu 500+ termen verbonden met de AAT. De laatste stand van zaken bekijk je op [https://api.triplydb.com/s/_pgDTKkMD](https://api.triplydb.com/s/_pgDTKkMD). In Poolparty kan je makkelijk nog meer relaties naar de AAT leggen.

# Verbinden met de GTAA

De GTAA is een [thesaurus van het Nederlands Instituut voor Beeld & Geluid](https://www.beeldengeluid.nl/kennis/kennisthemas/metadata/gemeenschappelijke-thesaurus-audiovisuele-archieven) en fungeert daar intern als termenlijst voor het classificeren van audio en beeldmateriaal. De thesaurus is opgedeeld in verschillende schema's, waarvan de lijst van Onderwerpen (https://data.beeldengeluid.nl/gtaa/Onderwerpen) mogelijk de interessantste is om naast de lijst van termen uit het Fotopersbureau De Boer te leggen. De verwachting is immers dat het beeldmateriaal uit het NHA van vergelijkbare aard is als de rapportages in de archieven van Beeld & Geluid, waarmee logischerwijs de gebruikte onderwerpstrefwoorden ook zouden moeten overlappen. 

Onze onderwerpstrefwoorden van De Boer koppelen aan de GTAA zou relevant zijn op twee fronten:
1. We maken onze NHA-collectie, via de LOD-principes, direct vergelijkbaar met andere collecties waarin geen AAT-verwijzingen zijn opgenomen, namelijk die van Beeld & Geluid en o.a. het Nationaal Archief.
2. Mogelijk kan onze collectie hiermee ingeladen worden in de [CLARIAH Media Suite](https://mediasuite.clariah.nl/), waarna het voor een gebruiker/onderzoeker mogelijk is om de hierin beschikbare tools te gebruiken om de collectie verder uit te diepen, te annoteren en te analyseren.

## Automatisch verbindingen leggen
Met relatief weinig moeite zou een link gelegd kunnen worden tussen de onderwerpen als we gebruik maken van het [OpenRefine Reconciliation API Endpoint](https://termennetwerk.netwerkdigitaalerfgoed.nl/reconciliation) van het [Termennetwerk](https://termennetwerk.netwerkdigitaalerfgoed.nl/). Om de data in OpenRefine te krijgen kunnen we een query schrijven die voor elk concept het label geeft en de hoofdcategorie waar het concept zich in bevindt: https://api.triplydb.com/s/VCEbGH8I2

```SPARQL
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?uri ?label ?category WHERE {  
  ?uri a skos:Concept ;
      skos:prefLabel ?label ;
      skos:broader* ?category_uri .
  
  ?category_uri skos:topConceptOf <https://digitaalerfgoed.poolparty.biz/nhaf/01617d03-bcd9-4720-9392-bf6bd92227b9> ;
      skos:prefLabel ?category .
} ORDER BY ?category ?label
```

Als voorbeeld de eerste 5 regels van het resultaat (totaal 1619 regels):

|uri                                                                            |label            |category    |
|-------------------------------------------------------------------------------|-----------------|------------|
|https://digitaalerfgoed.poolparty.biz/nhaf/6596e345-6d9e-d086-edb2-0d34f7a5b76f|1 mei viering    |Activiteiten|
|https://digitaalerfgoed.poolparty.biz/nhaf/e6c7073d-7cdc-fd32-c0a4-a6499a96e062|Aanbieden        |Activiteiten|
|https://digitaalerfgoed.poolparty.biz/nhaf/8483c868-f3b2-ed45-564e-5fb3319e4d47|Aankomst         |Activiteiten|
|https://digitaalerfgoed.poolparty.biz/nhaf/870f328b-5199-caa1-51bd-371b4ab4aa9c|Aanvaring schepen|Activiteiten|

Voor OpenRefine zijn de reconciliatie-API URLs:
* GTAA Onderwerpen: https://termennetwerk-api.netwerkdigitaalerfgoed.nl/reconcile/https://data.beeldengeluid.nl/id/datadownload/0031
* GTAA Namen: https://termennetwerk-api.netwerkdigitaalerfgoed.nl/reconcile/https://data.beeldengeluid.nl/id/datadownload/0030

Belangrijk hier is dat de optie `Reconcile against no particular type` aangeklikt wordt. 

Een totaal van 399 concepten kon met 100% overlap tussen de labels gematcht worden met de GTAA Onderwerpen. Daarnaast konden 106 concepten met 50-99% overlap verbonden worden. In veel gevallen zijn de onderwerpen van de GTAA specifieker dan de bredere termen van De Boer, zoals `Fietsen, fietspaden, fietsers` dat aan GTAA `fietspaden` en `fietsen` gekoppeld kan worden. Deze concepten zouden eigenlijk uitgesplitst moeten worden in de De Boer thesaurus, of via een `skos:narrowMatch` alsnog verbonden kunnen worden aan de GTAA. 

Koppelen van de resterende 1114 concepten aan de GTAA Namen levert 89 concepten op met 50-100% overlap op pref- of alternatieve labels. Hier staan concepten in zoals `Vleeshal`, `Velsertunnel` en `Kraantje Lek`. 

In totaal zijn hiermee 594 concepten gekoppeld aan GTAA concepten. Een overzicht is te vinden in `gtaa/concepts_link_gtaa.csv`. De links zijn in de thesaurus toegevoegd als `skos:closeMatch` relatie.




