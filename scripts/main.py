"""
Pipeline to process the data from the Fotopersbureau De Boer
collection of the Noord-Hollands Archief to RDF. Data are 
exported from Memorix Maior and are not included in any data
deposit.

Leon van Wissen, 2024-01-31
"""

import json
from itertools import count

import pandas as pd
from rdflib import (
    OWL,
    PROV,
    RDF,
    RDFS,
    SDO,
    SKOS,
    XSD,
    BNode,
    Dataset,
    Graph,
    Literal,
    Namespace,
    URIRef,
)
from rdflib.resource import Resource

HANDLE = Namespace("https://hdl.handle.net/21.12102/")
NHA = Namespace(
    "https://data.noord-hollandsarchief.nl/collection/FotopersbureauDeBoer/"
)
RANH = Namespace("https://maior-images.memorix.nl/ranh/iiif/")
PNV = Namespace("https://w3id.org/pnv#")
WD = Namespace("http://www.wikidata.org/entity/")
GTAA = Namespace("http://data.beeldengeluid.nl/gtaa/")
ROAR = Namespace("https://w3id.org/roar#")
GEO = Namespace("http://www.opengis.net/ont/geosparql#")
NHAT = Namespace("https://digitaalerfgoed.poolparty.biz/nha/")
RICO = Namespace("https://www.ica.org/standards/RiC/ontology#")
AAT = Namespace("http://vocab.getty.edu/aat/")

with open("scripts/series2collection.json") as infile:
    series2collection = json.load(infile)

location_type2concept = {
    "Adres": "http://vocab.getty.edu/aat/300386983",
    "Gemeente": "http://vocab.getty.edu/aat/300387330",
    "Land": "http://vocab.getty.edu/aat/300387392",
    "Object": "http://vocab.getty.edu/aat/300422821",
    "Park": "http://vocab.getty.edu/aat/300008187",
    "Plaats": "http://vocab.getty.edu/aat/300387331",
    "Regio": "http://vocab.getty.edu/aat/300182722",
    "Straat": "http://vocab.getty.edu/aat/300008247",
    "Water": "http://vocab.getty.edu/aat/300266059",
    "Wegen": "http://vocab.getty.edu/aat/300008217",
    "Wijk": "http://vocab.getty.edu/aat/300000762",
}


def process_photos(csv_path: str, graph_identifier: str, split_by: int = 50_000):
    """
    Process photograph data from a CSV file.

    Every photo is modelled as a SDO.Photograph. A file is created for
    every 60k (or a different 'split_by' argument value) resources.
    Incorporated are mappings from photo to HisVis AI concepts, reports,
    and the IIIF Image API description.

    Example output, serialized as RDF Turtle:

    ```turtle
    <https://hdl.handle.net/21.12102/a55d7380-e5b6-aaee-94ae-8f03096b77a4> a schema:Photograph ;
        schema:about [ a schema:Role ;
                schema:about <https://digitaalerfgoed.poolparty.biz/nha/a2c47bdc-ae1f-8dd4-8e2d-3df8a28a03c6> ;
                rico:certainty "0.45"^^xsd:float ],
            [ a schema:Role ;
                schema:about <https://digitaalerfgoed.poolparty.biz/nha/f0881540-bb3e-3755-dbac-735be0b40890> ;
                rico:certainty "1.0"^^xsd:float ],
            [ a schema:Role ;
                schema:about <https://digitaalerfgoed.poolparty.biz/nha/c7d7de0a-1aad-64b8-4208-0d188cacef9d> ;
                rico:certainty "0.4"^^xsd:float ] ;
        schema:identifier "NL-HlmNHA_1478_13925B00_01" ;
        schema:image <https://maior-images.memorix.nl/ranh/iiif/9bc8e0c5-b530-2354-a20a-92ea12cf2f85> ;
        schema:isPartOf <https://data.noord-hollandsarchief.nl/collection/FotopersbureauDeBoer/report/c9a72d42-5843-b781-264c-632a381f9a1f> .

    <https://maior-images.memorix.nl/ranh/iiif/9bc8e0c5-b530-2354-a20a-92ea12cf2f85> a schema:ImageObject ;
        schema:contentUrl <https://maior-images.memorix.nl/ranh/iiif/9bc8e0c5-b530-2354-a20a-92ea12cf2f85/full/max/0/default.jpg> ;
        schema:thumbnailUrl <https://maior-images.memorix.nl/ranh/iiif/9bc8e0c5-b530-2354-a20a-92ea12cf2f85/full/,250/0/default.jpg> .

    ```

    Args:
        csv_path (str): Path to the CSV file
        graph_identifier (str): URI of the graph
        split_by (int, optional): Number of resources per file, defaults to 50_000.
    """

    file_counter = count(1)
    g = Graph(identifier=graph_identifier)  # empty graph

    df_photos = pd.read_csv(csv_path, sep=";", encoding="utf-8", low_memory=False)
    df_assets = pd.read_csv(
        "export/0_UUIDReportageFotosMetUUIDAsset20231207.csv",
        sep=";",
        encoding="utf-8",
        low_memory=False,
    )
    df_keywords = pd.read_csv(
        "export/0_UUIDRepFotosMetAiTrefwoorden20231218.csv",
        sep=";",
        encoding="utf-8",
        low_memory=False,
    )
    df_keywords.drop("AI keyword (connected by AI)-ordering", axis=1, inplace=True)

    df = pd.merge(df_photos, df_assets, how="left", on="uuid")
    df = pd.merge(df, df_keywords, how="left", on="uuid")

    # Reports
    photo2reportuuid = dict()
    df_reports = pd.read_csv(
        "export/0_UUIDMetadataMetRepFotos20231204.csv",
        sep=";",
        encoding="utf-8",
        low_memory=False,
    )
    for _, row in df_reports.iterrows():
        if pd.isna(row["Reportage fotos-uuid"]):
            continue

        for i in row["Reportage fotos-uuid"].split("|"):
            photo2reportuuid[i] = row["uuid"]

    # Only public photos
    for n, row in df[df["Toon op web"] == 1].iterrows():
        n += 1
        if pd.isna(row["Objectnummer"]) or "test" in row["Objectnummer"]:
            continue

        photo = Resource(g, HANDLE.term(row["uuid"]))
        photo.add(RDF.type, SDO.Photograph)
        photo.add(SDO.identifier, Literal(row["Objectnummer"]))

        # Report (photo isPartOf report)
        if row["uuid"] in photo2reportuuid:
            photo.add(
                SDO.isPartOf,
                NHA.term("report/" + photo2reportuuid[row["uuid"]]),
            )

        # OCR, let's leave this for a more IIIF Prezi approach
        # if not pd.isna(row["OCR"]):
        #     photo.add(SDO.text, Literal(row["OCR"]))

        # IIIF Image API
        if pd.isna(row["Linked media-uuid"]):
            continue
        full_image_uri = RANH.term(row["Linked media-uuid"] + "/full/max/0/default.jpg")
        thumb_image_uri = RANH.term(
            row["Linked media-uuid"] + "/full/,250/0/default.jpg"
        )
        image = Resource(g, RANH.term(row["Linked media-uuid"]))
        image.add(RDF.type, SDO.ImageObject)
        image.add(SDO.contentUrl, full_image_uri)
        image.add(SDO.thumbnailUrl, thumb_image_uri)

        g.add((HANDLE.term(row["uuid"]), SDO.image, image.identifier))

        # AI keywords
        if not pd.isna(row["AI keyword (connected by AI)-Trefwoord-uuid"]):
            keywords = row["AI keyword (connected by AI)-Trefwoord-uuid"].split("|")
            percentages = row["AI keyword (connected by AI)-Percentage"].split("|")

            for keyword, percentage in zip(keywords, percentages):
                p = int(percentage) / 100
                if p < 0.05:  # skip lower than 5%
                    continue

                role = Resource(g, BNode())
                role.add(RDF.type, SDO.Role)
                role.add(SDO.about, NHAT.term(keyword))
                role.add(RICO.certainty, Literal(p, datatype=XSD.float))

                photo.add(SDO.about, role.identifier)

        # Serialize in smaller bits
        if (split_by and n % split_by == 0) or n == len(df):
            print(f"Serializing {n}...")

            g.bind("nha", HANDLE)
            g.bind("ranh", RANH)
            g.bind("schema", SDO)
            g.bind("rico", RICO)

            g.serialize(
                f"nha_photos_{str(next(file_counter)).zfill(3)}.trig", format="trig"
            )
            g = Graph(identifier=graph_identifier)  # new empty graph


def process_reports(csv_path: str, g: Graph):
    """
    Process report data from a CSV file.

    Every report is modelled as a SDO.CreativeWork, with a
    schema:additionalType of <http://data.beeldengeluid.nl/gtaa/30294> (Reportage).
    Extra information is given on the subcollection (deelcollectie) and the embedding
    in the overal collection.

    Individual mapping files (CSV) are used to link the report to persons, locations,
    and concepts (through the schema:about property).

    Example output, serialized as RDF Turtle:

    ```turtle
    <https://data.noord-hollandsarchief.nl/collection/FotopersbureauDeBoer/report/c9a72d42-5843-b781-264c-632a381f9a1f> a schema:CreativeWork ;
        schema:about <https://data.noord-hollandsarchief.nl/collection/FotopersbureauDeBoer/location/0d7a7fe6-acd6-594b-b552-27e28fb46db1>,
            <https://data.noord-hollandsarchief.nl/collection/FotopersbureauDeBoer/person/observation/fa906ea0-8d10-11ee-9aac-ac1f6ba5b082>,
            <https://digitaalerfgoed.poolparty.biz/nha/a9208ebc-d5f7-3fe6-14c1-05a880ba0690>,
            <https://digitaalerfgoed.poolparty.biz/nha/acd4a20a-ec61-bc6e-01f0-412a54c37524> ;
        schema:additionalType gtaa:30294 ;
        schema:dateCreated "1957-03-11"^^xsd:date ;
        schema:identifier "18948" ;
        schema:isPartOf <https://data.noord-hollandsarchief.nl/collection/FotopersbureauDeBoer/serie/vlakfilms> ;
        schema:name "Romanschrijver Harry Mulisch op het dak van de Sint-Bavokerk in Haarlem" .

    <https://data.noord-hollandsarchief.nl/collection/FotopersbureauDeBoer/serie/vlakfilms> a schema:ArchiveComponent,
        schema:Collection ;
        schema:genre aat:300127350 ;
        schema:isPartOf <https://data.noord-hollandsarchief.nl/collection/FotopersbureauDeBoer/> ;
        schema:name "Vlakfilms"@nl .

    <https://data.noord-hollandsarchief.nl/collection/FotopersbureauDeBoer/> a schema:ArchiveComponent,
        schema:Collection ;
        schema:holdingArchive <https://ror.org/03fsb6681> ;
        schema:name "Collectie Fotopersbureau De Boer" ;
        schema:url <https://noord-hollandsarchief.nl/collecties/beeld/collectie-fotopersbureau-de-boer> .
    ```

    Args:
        csv_path (str): Path to the CSV file
        g (Graph): A (named) graph

    """

    df = pd.read_csv(csv_path, sep=";", encoding="utf-8", low_memory=False)

    organization = Resource(g, URIRef("https://ror.org/03fsb6681"))  # ROR
    organization.add(RDF.type, SDO.ArchiveOrganization)
    organization.add(SDO.name, Literal("Noord-Hollands Archief"))
    organization.add(SDO.url, URIRef("https://noord-hollandsarchief.nl/"))

    collection = Resource(g, NHA.term(""))
    collection.add(RDF.type, SDO.Collection)
    collection.add(RDF.type, SDO.ArchiveComponent)
    collection.add(SDO.name, Literal("Collectie Fotopersbureau De Boer"))
    collection.add(
        SDO.url,
        URIRef(
            "https://noord-hollandsarchief.nl/collecties/beeld/collectie-fotopersbureau-de-boer"
        ),
    )
    collection.add(SDO.holdingArchive, organization.identifier)

    # Deelcollecties
    for values in series2collection.values():
        for value in values:
            deelcollectie = Resource(g, NHA.term("serie/" + value["@id"]))
            deelcollectie.add(RDF.type, SDO.Collection)
            deelcollectie.add(RDF.type, SDO.ArchiveComponent)
            deelcollectie.add(SDO.name, Literal(value["name"], lang="nl"))
            deelcollectie.add(SDO.isPartOf, collection.identifier)
            deelcollectie.add(SDO.genre, URIRef(value["genre"]))

    g.add((URIRef("http://data.beeldengeluid.nl/gtaa/30294"), RDF.type, SKOS.Concept))
    g.add(
        (
            URIRef("http://data.beeldengeluid.nl/gtaa/30294"),
            SKOS.prefLabel,
            Literal("Reportage", lang="nl"),
        )
    )

    for _, row in df.iterrows():
        report = Resource(g, NHA.term("report/" + row["uuid"]))
        report.add(RDF.type, SDO.CreativeWork)  # Collection?
        report.add(
            SDO.additionalType, URIRef("http://data.beeldengeluid.nl/gtaa/30294")
        )

        if not pd.isna(row["Invoernummer onderwerpskaarten"]):
            for i in row["Invoernummer onderwerpskaarten"].split("|"):
                report.add(SDO.identifier, Literal(i))
        elif not pd.isna(row["Logboek pagina ID"]):
            report.add(SDO.identifier, Literal(row["Logboek pagina ID"]))

        if not pd.isna(row["Beschrijving"]):
            report.add(SDO.name, Literal(row["Beschrijving"]))

        try:
            if not pd.isna(row["Datum"]):
                for i in row["Datum"].split("|"):
                    if i and "/" in i:
                        d, m, y = i.split("/")
                    elif i and "-" in i:
                        d, m, y = i.split("-")
                    else:
                        continue

                    if d == "00" and m == "00":
                        report.add(SDO.dateCreated, Literal(f"{y}", datatype=XSD.gYear))
                    elif d == "00":
                        report.add(
                            SDO.dateCreated,
                            Literal(f"{y}-{m}", datatype=XSD.gYearMonth),
                        )
                    elif y == "0000":
                        continue
                    else:
                        report.add(
                            SDO.dateCreated, Literal(f"{y}-{m}-{d}", datatype=XSD.date)
                        )
        except:
            print(row["Datum"])

        # Collection
        if not pd.isna(row["Deelcollectie"]):
            for i in series2collection[row["Deelcollectie"]]:
                report.add(SDO.isPartOf, NHA.term("serie/" + i["@id"]))

    ## Persons
    df = pd.read_csv(
        "export/2_UUIDMetadataMetPersonenObs20231128.csv",
        sep=";",
        encoding="utf-8",
        low_memory=False,
    )

    for _, row in df.iterrows():
        if pd.isna(row["Persoon observaties-uuid"]):
            continue
        for i in row["Persoon observaties-uuid"].split("|"):
            g.add(
                (
                    NHA.term("report/" + row["uuid"]),
                    SDO.about,
                    NHA.term("person/observation/" + i),
                )
            )

    ## Locations
    df = pd.read_csv(
        "export/2_UUIDMetadataMetLocaties20231214.csv",
        sep=";",
        encoding="utf-8",
        low_memory=False,
    )

    for _, row in df.iterrows():
        if pd.isna(row["Locaties-Locatie-uuid"]):
            continue
        for i in row["Locaties-Locatie-uuid"].split("|"):
            g.add(
                (
                    NHA.term("report/" + row["uuid"]),
                    SDO.about,
                    NHA.term("location/" + i),
                )
            )

    # Subjects
    df = pd.read_csv(
        "export/2_UUIDMetadataMetCataloguskaart20231214.csv",
        sep=";",
        encoding="utf-8",
        low_memory=False,
    )
    for _, row in df.iterrows():
        if pd.isna(row["Catalogus kaart-Catalogus kaart-uuid"]):
            continue
        for i in row["Catalogus kaart-Catalogus kaart-uuid"].split("|"):
            g.add(
                (
                    NHA.term("report/" + row["uuid"]),
                    SDO.about,
                    NHAT.term(i),
                )
            )


def process_catalog_cards(csv_path: str, g: Graph):
    """
    Process catalog card data from a CSV file.

    Every catalog card (the origin of concepts in the thesaurus)
    is modelled as a SDO.CreativeWork, with a schema:additionalType
    pointing to <http://vocab.getty.edu/aat/300026769> (Cataloguskaart).
    The link with the concept is made through the schema:about property.

    Example output, serialized as RDF Turtle:

    ```turtle
    <https://data.noord-hollandsarchief.nl/collection/FotopersbureauDeBoer/catalog/a9208ebc-d5f7-3fe6-14c1-05a880ba0690> a schema:CreativeWork ;
        schema:about <https://digitaalerfgoed.poolparty.biz/nha/a9208ebc-d5f7-3fe6-14c1-05a880ba0690> ;
        schema:additionalType aat:300026769 ;
        schema:name "Portretten" ;
        schema:temporalCoverage "1947/1989" .
    ```

    Args:
        csv_path (str): Path to the CSV file
        g (Graph): A (named) graph

    """

    df = pd.read_csv(csv_path, sep=";", encoding="utf-8", low_memory=False)

    g.add((URIRef("http://vocab.getty.edu/aat/300026769"), RDF.type, SKOS.Concept))
    g.add(
        (
            URIRef("http://vocab.getty.edu/aat/300026769"),
            SKOS.prefLabel,
            Literal("Cataloguskaart", lang="nl"),
        )
    )

    for _, row in df.iterrows():
        card = Resource(g, NHA.term("catalog/" + row["uuid"]))
        card.add(RDF.type, SDO.CreativeWork)
        card.add(SDO.additionalType, URIRef("http://vocab.getty.edu/aat/300026769"))

        card.add(SDO.name, Literal(row["Titel"]))

        if not pd.isna(row["Beginjaar"]) and not pd.isna(row["Eindjaar"]):
            coverage = f"{int(row['Beginjaar'])}/{int(row['Eindjaar'])}"
        elif not pd.isna(row["Beginjaar"]):
            coverage = f"{int(row['Beginjaar'])}"
        elif not pd.isna(row["Eindjaar"]):
            coverage = f"{int(row['Eindjaar'])}"

        if coverage:
            card.add(
                SDO.temporalCoverage,
                Literal(coverage),
            )

        # Link NHA Thesaurus-identifier
        pp_uri = URIRef(row["Link NHA Thesaurus-identifier"].split(":", 1)[1])
        card.add(SDO.about, pp_uri)


def process_locations(csv_path, g: Graph):
    """
    Process location data from a CSV file.

    Every location is modelled as a SDO.Place. An additional type
    is added with a link to the AAT. The geometry is added as a
    geosparql Geometry in WKT.

    Example output, serialized as RDF Turtle:

    ```turtle
    <https://data.noord-hollandsarchief.nl/collection/FotopersbureauDeBoer/location/0d7a7fe6-acd6-594b-b552-27e28fb46db1> a schema:Place ;
        geo:hasGeometry [ a geo:Geometry ;
                geo:asWKT "POINT(4.6359055555556 52.381366666667)"^^geo:wktLiteral ] ;
        owl:sameAs wd:Q1083850 ;
        schema:additionalType aat:300008247 ;
        schema:name "Grote Markt" .

    aat:300008247 a skos:Concept ;
        skos:prefLabel "Straat" .
    ```

    Args:
        csv_path (str): Path to the CSV file
        g (Graph): A (named) graph

    """
    for key, value in location_type2concept.items():
        concept = Resource(g, URIRef(value))
        concept.add(RDF.type, SKOS.Concept)
        concept.add(SKOS.prefLabel, Literal(key))

    df = pd.read_csv(
        csv_path,
        sep=";",
        encoding="utf-8",
        low_memory=False,
    )

    for _, row in df.iterrows():
        location = Resource(g, NHA.term("location/" + row["uuid"]))
        location.add(RDF.type, SDO.Place)
        location.add(SDO.additionalType, URIRef(location_type2concept[row["Soort"]]))

        address = Resource(g, BNode())
        address.add(RDF.type, SDO.PostalAddress)

        if not pd.isna(row["Land"]):
            address.add(SDO.addressCountry, Literal(row["Land"]))

        if not pd.isna(row["Plaats"]):
            address.add(SDO.addressLocality, Literal(row["Plaats"]))

        if not pd.isna(row["Straat"]):
            if (
                not pd.isna(row["Huisnummer"])
                and not pd.isna(row["Huisletter"])
                and not pd.isna(row["Huisnummertoevoeging"])
            ):
                street = f"{row['Straat']} {row['Huisnummer']}{row['Huisletter']} {row['Huisnummertoevoeging']}"
            elif not pd.isna(row["Huisnummer"]) and not pd.isna(row["Huisletter"]):
                street = f"{row['Straat']} {row['Huisnummer']}{row['Huisletter']}"
            elif not pd.isna(row["Huisnummer"]):
                street = f"{row['Straat']} {row['Huisnummer']}"
            else:
                street = row["Straat"]

            address.add(SDO.streetAddress, Literal(street))

        # Name
        if row["Soort"] == "Adres" and not pd.isna(row["Straat"]):
            location.add(SDO.name, Literal(street))
        else:
            location.add(SDO.name, Literal(row.get(row["Soort"], "?")))

        if not pd.isna(row["WikiData ID"]):
            location.add(OWL.sameAs, WD.term(row["WikiData ID"]))

        # Geometry
        if not pd.isna(row["Coordinates-wkt"]):
            geo = Resource(g, BNode())
            geo.add(RDF.type, GEO.term("Geometry"))
            geo.add(GEO.asWKT, Literal(row["Coordinates-wkt"], datatype=GEO.wktLiteral))

            location.add(GEO.hasGeometry, geo)


def process_person_observations(
    csv_path: str, csv_path_mapping: str, g: Graph, g_reconstructions: Graph
):
    """
    Process person observation data from a CSV file.

    Every person observation is modelled as a ROAR.PersonObservation and
    only if the person is a 'public person' (agreed upon by the NHA during
    the project). The observation contains information on how the person was
    mentioned in the report. For name elements, the PNV properties are used
    in a PNV.PersonName resource.

    The person observation is linked to a person reconstruction through a
    PROV.wasDerivedFrom property. This mapping comes from a separate CSV file
    and is added to the named graph with person reconstructions.

    Example output, serialized as RDF Turtle:

    ```turtle
    <https://data.noord-hollandsarchief.nl/collection/FotopersbureauDeBoer/person/observation/fa906ea0-8d10-11ee-9aac-ac1f6ba5b082> a roar:PersonObservation ;
        rdfs:label "Mulisch, Harry" ;
        schema:name "Harry Mulisch" ;
        pnv:hasName [ a pnv:PersonName ;
                pnv:baseSurname "Mulisch" ;
                pnv:givenName "Harry" ;
                pnv:literalName "Harry Mulisch" ] .
    ```

    Args:
        csv_path (str): Path to the CSV file
        csv_path_mapping (str): Path to the CSV file with the mapping to reconstructions
        g (Graph): A (named) graph for the person observations
        g_reconstructions (Graph): A (named) graph for the person reconstructions
    """

    df = pd.read_csv(
        csv_path,
        sep=";",
        encoding="utf-8",
        low_memory=False,
    )

    # Only for 'public persons'
    for _, row in df[df["Publiek persoon"] == 1].iterrows():
        person = Resource(
            g,
            NHA.term("person/observation/" + row["uuid"]),
        )
        person.add(RDF.type, ROAR.PersonObservation)
        person.add(SDO.name, Literal(row["Label observatie"]))
        person.add(RDFS.label, Literal(row["prefLabel"]))

        pn = Resource(g, BNode())
        pn.add(RDF.type, PNV.PersonName)

        if not pd.isna(row["Voornaam (pnv:givenName)"]):
            pn.add(PNV.givenName, Literal(row["Voornaam (pnv:givenName)"]))

        if not pd.isna(row["Achternaam (pnv:baseSurname)"]):
            pn.add(PNV.baseSurname, Literal(row["Achternaam (pnv:baseSurname)"]))

        if not pd.isna(row["Prefix (pnv:prefix)"]):
            pn.add(PNV.prefix, Literal(row["Prefix (pnv:prefix)"]))

        if not pd.isna(row["Initialen (pnv:initials)"]):
            pn.add(PNV.initials, Literal(row["Initialen (pnv:initials)"]))

        if not pd.isna(row["Infix (pnv:infixTitle)"]):
            pn.add(PNV.infixTitle, Literal(row["Infix (pnv:infixTitle)"]))

        if not pd.isna(row["Tussenvoegsel (pnv:surnamePrefix)"]):
            pn.add(PNV.surnamePrefix, Literal(row["Tussenvoegsel (pnv:surnamePrefix)"]))

        if not pd.isna(row["Patroniem (pnv:patronym)"]):
            pn.add(PNV.patronym, Literal(row["Patroniem (pnv:patronym)"]))

        if not pd.isna(
            row["Onderscheidend achtervoegsel (pnv:disambiguatingDescription)"]
        ):
            pn.add(
                PNV.disambiguatingDescription,
                Literal(
                    row["Onderscheidend achtervoegsel (pnv:disambiguatingDescription)"]
                ),
            )

        pn.add(PNV.literalName, Literal(row["Volledige naam (pnv:literalName)"]))

        person.add(PNV.hasName, pn)

    # Mapping to observations
    df_mapping = pd.read_csv(
        csv_path_mapping,
        sep=";",
        encoding="utf-8",
        low_memory=False,
    )

    publieke_personen = df[df["Publiek persoon"] == 1]["uuid"].values

    for _, row in df_mapping.iterrows():
        if pd.isna(row["Persoon reconstructie-uuid"]):
            continue
        elif row["uuid"] not in publieke_personen:  # only public persons
            continue
        g_reconstructions.add(
            (
                NHA.term("person/reconstruction/" + row["Persoon reconstructie-uuid"]),
                PROV.wasDerivedFrom,
                NHA.term("person/observation/" + row["uuid"]),
            )
        )


def process_person_reconstructions(csv_path: str, g: Graph):
    """
    Process person reconstruction data from a CSV file.

    Every person reconstruction is modelled as a ROAR.PersonReconstruction.
    The person reconstruction contains information on the person, such as
    (preferred) name, birth and death dates and places, occupation, and an
    external identifier (Wikidata). The reconstruction is only modelled if
    the person is a 'public person' (agreed upon by the NHA during the project).

    When running this function after the person observation function, the person
    reconstructions are already linked to the person observations through a
    PROV.wasDerivedFrom property.

    Example output, serialized as RDF Turtle:

    ```turtle
    <https://data.noord-hollandsarchief.nl/collection/FotopersbureauDeBoer/person/reconstruction/67688614-5a70-5835-87a5-67b63ee56ee6> a schema:Person,
            roar:PersonReconstruction ;
        owl:sameAs gtaa:134822,
            wd:Q927 ;
        prov:wasDerivedFrom <https://data.noord-hollandsarchief.nl/collection/FotopersbureauDeBoer/person/observation/fa906ea0-8d10-11ee-9aac-ac1f6ba5b082> ;
        schema:birthDate "1927-07-29"^^xsd:date ;
        schema:birthPlace "Haarlem" ;
        schema:deathDate "2010-10-30"^^xsd:date ;
        schema:deathPlace "Amsterdam" ;
        schema:description "Nederlands schrijver (1927–2010)" ;
        schema:hasOccupation "dichter",
            "essayist",
            "romanschrijver",
            "scenarioschrijver",
            "schrijver",
            "toneelschrijver" ;
        schema:name "Harry Mulisch" ;
        pnv:hasName [ a pnv:PersonName ;
                pnv:baseSurname "Mulisch" ;
                pnv:givenName "Harry" ;
                pnv:literalName "Harry Mulisch" ] .
    ```

    Args:
        csv_path (str): Path to the CSV file
        g (Graph): A (named) graph for the person reconstructions
    """

    df = pd.read_csv(
        csv_path,
        sep=";",
        encoding="utf-8",
        low_memory=False,
    )

    # Only for 'public persons'
    for _, row in df[df["Publiek persoon"] == 1].iterrows():
        person = Resource(
            g,
            NHA.term("person/reconstruction/" + row["uuid"]),
        )
        person.add(RDF.type, ROAR.PersonReconstruction)
        person.add(RDF.type, SDO.Person)
        person.add(SDO.name, Literal(row["Label"]))

        if not pd.isna(row["Beschrijving"]):
            person.add(SDO.description, Literal(row["Beschrijving"]))

        if not pd.isna(row["Geboortedatum"]):
            person.add(SDO.birthDate, Literal(row["Geboortedatum"], datatype=XSD.date))

        if not pd.isna(row["Geboorteplaats"]):
            person.add(SDO.birthPlace, Literal(row["Geboorteplaats"]))

        if not pd.isna(row["Overlijdensdatum"]):
            person.add(
                SDO.deathDate, Literal(row["Overlijdensdatum"], datatype=XSD.date)
            )

        if not pd.isna(row["Overlijdensplaats"]):
            person.add(SDO.deathPlace, Literal(row["Overlijdensplaats"]))

        if not pd.isna(row["Beroep"]):
            for i in row["Beroep"].split("|"):
                person.add(SDO.hasOccupation, Literal(i))

        if not pd.isna(row["Wikidata ID"]):
            person.add(OWL.sameAs, WD.term(row["Wikidata ID"]))

        pn = Resource(g, BNode())
        pn.add(RDF.type, PNV.PersonName)

        if not pd.isna(row["Voornaam (pnv:givenName)"]):
            pn.add(PNV.givenName, Literal(row["Voornaam (pnv:givenName)"]))

        if not pd.isna(row["Achternaam (pnv:baseSurname)"]):
            pn.add(PNV.baseSurname, Literal(row["Achternaam (pnv:baseSurname)"]))

        if not pd.isna(row["Prefix (pnv:prefix)"]):
            pn.add(PNV.prefix, Literal(row["Prefix (pnv:prefix)"]))

        if not pd.isna(row["Initialen (pnv:initials)"]):
            pn.add(PNV.initials, Literal(row["Initialen (pnv:initials)"]))

        if not pd.isna(row["Infix (pnv:infixTitle)"]):
            pn.add(PNV.infixTitle, Literal(row["Infix (pnv:infixTitle)"]))

        if not pd.isna(row["Tussenvoegsel (pnv:surnamePrefix)"]):
            pn.add(PNV.surnamePrefix, Literal(row["Tussenvoegsel (pnv:surnamePrefix)"]))

        if not pd.isna(row["Patroniem (pnv:patronym)"]):
            pn.add(PNV.patronym, Literal(row["Patroniem (pnv:patronym)"]))

        if not pd.isna(
            row["Onderscheidend achtervoegsel (pnv:disambiguatingDescription)"]
        ):
            pn.add(
                PNV.disambiguatingDescription,
                Literal(
                    row["Onderscheidend achtervoegsel (pnv:disambiguatingDescription)"]
                ),
            )

        pn.add(PNV.literalName, Literal(row["Volledige naam (pnv:literalName)"]))

        person.add(PNV.hasName, pn)


def process_gtaa(mapping_file: str, g: Graph):
    """
    Add extra GTAA links to person and location resources.

    Since we, for locations and person reconstructions, only linked
    to Wikidata, a GTAA link is missing in the original data. And
    since we _did_ link to the GTAA in the thesaurus, this function
    adds the GTAA link to the resources, based on a mapping from
    Wikidata to the GTAA.

    Args:
        mapping_file (str): Filepath to the mapping file (json)
        g (Graph): A graph with person or location resources
    """
    with open(mapping_file) as f:
        mapping = json.load(f)

    for wd_id, gtaa_ids in mapping.items():
        # find resource and add gtaa to NHA resource
        for s in g.subjects(OWL.sameAs, WD.term(wd_id)):
            for i in gtaa_ids:
                g.add((s, OWL.sameAs, GTAA.term(i)))


def main():
    ds = Dataset()

    # 0. Foto's
    g_identifier = NHA.term("photograph/")
    print("Processing photos...")
    process_photos("export/0_Reportagefotos20231128.csv", g_identifier, split_by=60_000)

    # 2. Metadata De Boer (reportages)
    g = ds.graph(identifier=NHA.term("report/"))
    print("Processing reports...")
    process_reports("export/2_MetadataDeBoer20231128.csv", g)

    # 3. Cataloguskaarten
    g = ds.graph(identifier=NHA.term("catalog/"))
    print("Processing catalog cards...")
    process_catalog_cards("export/3_Cataloguskaarten20231128.csv", g)

    # 4. Locaties
    g = ds.graph(identifier=NHA.term("location/"))
    print("Processing locations...")
    process_locations("export/4_LocatiesMetCoordinaten20231213.csv", g)
    process_gtaa("scripts/wd2gtaa.json", g)

    # 5. Personen (observaties)
    g = ds.graph(identifier=NHA.term("person/observation/"))
    g_reconstructions = ds.graph(identifier=NHA.term("person/reconstruction/"))
    print("Processing person observations...")
    process_person_observations(
        "export/5_PersoonObservaties20231128.csv",
        "export/5_UUIDPersoonObsMetRec20231128.csv",
        g,
        g_reconstructions,
    )

    # 6. Personen (reconstructies)
    g = ds.graph(identifier=NHA.term("person/reconstruction/"))
    print("Processing person reconstructions...")
    process_person_reconstructions("export/6_PersoonReconstructies20231128.csv", g)
    process_gtaa("scripts/wd2gtaa.json", g)

    ds.bind("pnv", PNV)
    ds.bind("wd", WD)
    ds.bind("owl", OWL)
    ds.bind("schema", SDO)
    ds.bind("roar", ROAR)
    ds.bind("prov", PROV)
    ds.bind("nha", HANDLE)
    ds.bind("ranh", RANH)
    ds.bind("rico", RICO)
    ds.bind("skos", SKOS)
    ds.bind("xsd", XSD)
    ds.bind("nhat", NHAT)
    ds.bind("report", NHA.term("report/"))
    ds.bind("catalog", NHA.term("catalog/"))
    ds.bind("location", NHA.term("location/"))
    ds.bind(
        "personobservation",
        NHA.term("person/observation/"),
    )
    ds.bind(
        "personreconstruction",
        NHA.term("person/reconstruction/"),
    )
    ds.bind("subject", NHA.term("subject/"))
    ds.bind("gtaa", GTAA)
    ds.bind("geo", GEO)
    ds.bind("aat", AAT)

    print()
    print("Serializing...")

    # Serialize with a nice name
    for g in ds.graphs():
        if str(g.identifier) == "urn:x-rdflib:default":
            continue
        name = g.identifier.split(NHA.term(""))[1].replace("/", "")

        print(f"Serializing {name}...")
        g.serialize(f"nha_{name}.trig", format="trig")


if __name__ == "__main__":
    main()
