# Termen FAIR Photos

Er waren bij aanvang van het project twee termenlijsten beschikbaar:

## Scene detection

Dit is een set van 143 tags, toegekend via een geautomatiseerd beeldherkenningsproces door het project HisVis. Meer informatie hierover is te lezen op de [website van het Noord-Hollands Archief](https://noord-hollandsarchief.nl/nieuws/nieuwsoverzicht/1154-historische-fotos-beter-doorzoekbaar-met-ai) of in de publicatie:
* Melvin Wevers, Nico Vriend en Alexander de Bruin, [_What to do with 2.000.000 Historical Press Photos? The Challenges and Opportunities of Applying a Scene Detection Algorithm to a Digitised Press Photo Collection_](https://dx.doi.org/10.18146/tmg.815), in: TMG Journal for Media History, volume 25, nummer 1 (2022)

De termen:
- zijn niet hiërarchisch geordend
- zijn niet verbonden met externe concepten
- zijn toegekend aan individuele foto's
- zijn via een beschrijving aan gerelateerde concepten verbonden (e.g. "Het label 'Duinen' heeft mogelijk overeenkomsten met het label 'Strand'")
- hebben Nederlandse en Engelse labels en beschrijvingen
- zijn elk voorzien van een voorbeeldfoto die uitbeeldt wat deze term uitdrukt

## Catalogus De Boer

Dit is een set van [1.591 termen](catalogus-de-boer/deboer-concepts.csv), toegekend door medewerkers van Persbureau De Boer. Je kunt de termen en de daarmee verbonden foto's bekijken op [https://noord-hollandsarchief.nl/beelden/beeldbankdeboer/](https://noord-hollandsarchief.nl/beelden/beeldbankdeboer/). De termen:

- zijn niet hiërarchisch geordend
- zijn niet verbonden met externe concepten
- zijn toegekend aan reportages (en via die route aan alle individuele foto's binnen die reportages)
- zijn soms ambigu ('mijnen' voor zowel zee- als staatsmijnen, 'graven' voor zowel graafwerkzaamheden als laatste rustplaatsen)
- komen soms dubbel voor, zie lijstje op [https://api.triplydb.com/s/FJ0Myfn52](https://api.triplydb.com/s/FJ0Myfn52)
- kunnen zowel algemene concepten beschrijven ('kerk', 'schoolvoetbal', 'chocolade') als specifieke locaties, personen en organisaties ('Ruigoord', 'Wiesman', 'Voetbal Telstar')

In dit project willen we de termen

- zoveel mogelijk hiërarchisch ordenen (we doen dit in de [PoolParty](https://digitaalerfgoed.poolparty.biz/nhaf.html)-instantie van de [RCE](https://netwerkdigitaalerfgoed.nl/nieuws/lets-poolparty-samenwerken-aan-een-thesaurus/))
- verbinden met de [AAT](https://www.getty.edu/vow/AATHierarchy?find=&logic=AND&note=&subjectid=300000000) - meer hierover op [catalogus-de-boer/README.md](catalogus-de-boer/README.md)
- dubbel voorkomende termen samenvoegen (met behoud van links naar reportages)
- ambigue termen splitsen?
- indien specifieke locaties, overhevelen naar geografische thesaurus en hier verwijderen?
- 'skos:related' links leggen, wellicht automatisch door te kijken naar welke termen frequent vaak samen voorkomen op de 2M foto's

