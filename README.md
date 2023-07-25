# FAIR Photos

Het project behelst het toegankelijker maken van de collectie De Boer op de volgende manieren:

- [Termenlijsten](concepts)
- Locaties
- Personen

## Overzicht

![](https://www.plantuml.com/plantuml/svg/jLHVRzCm47_Ffx2s1pgaYlTgcWP52AJ1q2JW-M9V4XF75zcNRDEqxuxJrAjTgkK5NXhxvyllpzMNQy_WUEXCqMY5Gced3HO5MjRyACwsP0nArdWcm0iPT-BSwBhXqWmedWeXtefXq2eirklm8qJnVA3uH4nYfNIj6S1Sx8Yg2JltO3go9mXwT1qORLknQi0gWnS1XAf4D4hREcmOMy-vpZUiWJLM8nf1bL0QnAfwz1hRMTCcv-Vt3G8VAwTiTz3tv1ZgERcBsn2T6-tPd0h-0RridFuzpYO_GcXiU6v9uVI8tPjqYeFK3Kc87JPXlTXV2p3HraWTijCJjuSEttkn-gLRhO3X8ito7PqdifvAZsvyqUfd-BRqhykDH6uloOFtQ4V2sgC9Uv0DOpmSftnArpWRF670eGo_x0PvvE4EvN_niD2OMwlGtQFhTruexavRsIr-t7s9bdnBVjCxh6wWH1C1C9pjyG4aVmMMJKIa8OyPOi4vki-WqX6e6NbExyfdxNzgBtBZpVXFh2kijDMioGQa8gW2qciv0Rc9BJ0OgWVV0ZZEfqpcPyk3TaDrITZcB6OFBh--9Ikn3oRmWT7PlOaz-BGG_3b0nM6qGytGhzTNX-_SPhuK2j684MnHLCGKoz8loaP0rLBdMTUxmkH8JAK7aMFAL3yKJW8RqI1Ml5k_yLb5u8hVY8se0LZGYEwe8fdiLufUxanQ4mDU9PSgBqWcTcf3BWPLZGQrcfEz44o4yK_P_3K5KMcnC26yp1CaGuFkNJ9Kw3BwoopPmejvmqnuStyjyvnvpAC1E6v9SOrM3Ptv0m00)

<details>
  
  ```plantuml
  @startuml
  hide circle
  
  entity "Collectie" as collectie #lightblue {
    * uuid
    --
      
  }
  
  entity "Foto (digitaal)" as foto #salmon {
    * uuid
    --
    permalink (handle)
    afbeelding
    tekst  
  }
  
  entity "Negatiefvel of dia (fysiek)" as negatiefvel #wheat {
    * uuid
    --
  }
  
  entity "Rapportage" as rapportage #thistle {
    * uuid
    --
    Beschrijving
    Datum
    Code
    Collectie
  }
  
  
  
  
  entity "Locatie" as locatie #lightblue {
    * uuid
    --
    naam
    geometrie
    sameAs (Wikidata)
  }
  
  entity "Persoonsobservatie" as persoonObs #lightblue {
    * uuid
    --
    voornaam
    tussenvoegsel
    achternaam
    volledige naam
  }
  
  entity "Persoonsreconstructie" as persoonRec #lightblue {
    * uuid
    --
    voornaam
    tussenvoegsel
    achternaam
    volledige naam
    sameAs (Wikidata)
  }
  
  entity "Onderwerp" as onderwerp #lightblue {
    * uuid
    * URI
    --
    skos:prefLabel
    skos:altLabel
    skos:exactMatch
    skos:closeMatch
    skos:narrowMatch
    skos:broadMatch
  }
  
  
  
  entity "HisVis Onderwerp" as hvonderwerp #lightblue {
    * uuid
    * URI
    --
    skos:prefLabel
    skos:definition
    foaf:depiction
  }
  
  
  
  entity "Cataloguskaart (fysiek)" as cataloguskaart #wheat {
    * uuid
    --
  }
  
  entity "Logboek (fysiek)" as logboek #wheat {
    * uuid
    --
  }
  
  entity "Concept (extern)" as concept {
    * URI
    --
    skos:prefLabel
  }
    
  rapportage --up--> collectie: onderdeel van
  
  foto --up--> negatiefvel: afkomstig van
  negatiefvel --> rapportage: onderdeel van
  
  rapportage -> foto: heeft foto's
  
  rapportage --> locatie: gaat over
  rapportage --> persoonObs: gaat over
  rapportage --> onderwerp: gaat over
  
  foto --> hvonderwerp: gaat over
  
  persoonRec -up-> persoonObs: afgeleid van
  
  onderwerp --> concept: skos:closeMatch
  hvonderwerp --> concept: skos:closeMatch
  
  onderwerp <--> onderwerp: skos:broader/skos:narrower
  hvonderwerp <--> hvonderwerp: skos:broader/skos:narrower
  
  rapportage --l-> logboek: afgeleid van
  onderwerp --> cataloguskaart: afgeleid van
  
  
  @enduml
  ```

</details>
