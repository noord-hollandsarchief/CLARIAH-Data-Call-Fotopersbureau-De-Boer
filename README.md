# FAIR Photos

Het project behelst het toegankelijker maken van de collectie De Boer op de volgende manieren:

- [Termenlijsten](concepts)
- Locaties
- Personen

## Overzicht

![](https://www.plantuml.com/plantuml/svg/jLLXQyCs4Fs-No6Q3qi7OT_32DqwIiEwTHJMVRv8pxPcMJBIsMqf--zppaaSswHai46Wv-VdU-zEkgkwIqoHcyfzerHX3PIsKJjqJzqFdYr_g9lxu1mqMzmeIaeVdzJ2sRpWdMkWFZkwKj-ffh56mjLA_aYUlyVf7W87jJGsjqpaRYLfjiSMYLmL_CLaDM95plfIBGlonk5MOCfsW3FMvsgvtMuVUfHH9fQe8jQ5-YMIPmMlzlBV9dapz_ORScABh8LJ8LF6abfc7ycYx7twi_UBjmB45zrweae27GmaC80xTK-GaYYoRweASUxb1NM8J3b4EHwVr88BczXTRlfFIBg8zg_M-bo0ducRtilMjm6nLrJ16yGtn3g93_WvvHKEZzJn_DpVKz1ql1HEuckknD2N7A42nqCh4bNuCQdbdxQqXfXkvuA_8wOGV0gxXDYUjEiUVjwbQ-JR4EB90ZSfOLzldk048Lqm1a8Rd8EnESJsPKiHElZ4iT4JLo_G_xUhQzltV3nkyNSw_Cls9FpZPNjkD9KXhUk8x8bsS0D4ZYS8tadph_lP6p3jGi84ynHZU9k0knZ823RKCQxcqQPNczIugABzZyiooAotR8CNB0kKTLXjjK0NhDqJamjvqu_LU87eqRilTyXytl9TG3dEvthmNoMw3rwZxepXdH7zmTW1_BokGP9JifuMKqTjwjLgC_o7MFUtp01EjUJ5XQpw4_LidwuLPMMe4jky9u-MRKSUbAPvfpus8h9M1P2nnBBm9sOtihN4Pax4AhI8CygmNBvW3SCq9WtLReQhEIUTxugkBnDLod8uM7EgT52Jn8U3MyydJ3IleKxJ_Z2fQHX9nE_FXXPHH2OV2d3LfvC-EZaIkS-JiYSrJwPeHkv_T_2cgTm_)

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
    afbeelding (IIIF)
    tekst
    match Krant en Foto's
    
  }
  
  entity "Negatiefvel of dia (fysiek)" as negatiefvel #wheat {
    * uuid
    --
    naam
    code
    deelcollectie
    kaartnummer
  }
  
  entity "Reportage" as reportage #thistle {
    * uuid
    --
    Beschrijving
    Datum
    Invoernummer onderwerpskaarten
    Invoernummer VeleHanden
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
    
  reportage --up--> collectie: onderdeel van
  
  foto --up--> negatiefvel: afkomstig van
  negatiefvel --> reportage: onderdeel van
  
  reportage -> foto: heeft foto's
  
  reportage --> locatie: gaat over
  reportage --> persoonObs: gaat over
  reportage --> onderwerp: gaat over
  
  foto --> hvonderwerp: gaat over
  
  persoonRec -up-> persoonObs: afgeleid van
  
  onderwerp --> concept: skos:closeMatch
  hvonderwerp --> concept: skos:closeMatch
  
  onderwerp <--> onderwerp: skos:broader/skos:narrower
  hvonderwerp <--> hvonderwerp: skos:broader/skos:narrower
  
  reportage --l-> logboek: afgeleid van
  onderwerp --> cataloguskaart: afgeleid van
  
  
  @enduml
  ```

</details>
