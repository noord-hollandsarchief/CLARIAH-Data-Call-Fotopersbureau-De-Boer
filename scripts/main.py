import json
from itertools import count


from rdflib import (
    Dataset,
    Graph,
    Namespace,
    Literal,
    URIRef,
    RDF,
    RDFS,
    SKOS,
    XSD,
    SDO,
    OWL,
    PROV,
    BNode,
)
from rdflib.resource import Resource

import pandas as pd

HANDLE = Namespace("https://hdl.handle.net/21.12102/")
RANH = Namespace("https://maior-images.memorix.nl/ranh/iiif/")
PNV = Namespace("https://w3id.org/pnv#")
WD = Namespace("http://www.wikidata.org/entity/")
GTAA = Namespace("http://data.beeldengeluid.nl/gtaa/")
ROAR = Namespace("https://w3id.org/roar#")
GEO = Namespace("http://www.opengis.net/ont/geosparql#")
NHAT = Namespace("https://digitaalerfgoed.poolparty.biz/nha/")
RICO = Namespace("https://www.ica.org/standards/RiC/ontology#")
AAT = Namespace("http://vocab.getty.edu/aat/")

series2collection = {
    "B": [
        {
            "@id": "vlakfilms",
            "name": "Vlakfilms",
            "genre": "http://vocab.getty.edu/aat/300127350",
        }
    ],
    "BD": [
        {
            "@id": "vlakfilms",
            "name": "Vlakfilms",
            "genre": "http://vocab.getty.edu/aat/300127350",
        }
    ],
    "BG": [
        {
            "@id": "vlakfilms",
            "name": "Vlakfilms",
            "genre": "http://vocab.getty.edu/aat/300127350",
        }
    ],
    "C": [
        {
            "@id": "glasnegatieven",
            "name": "Glasnegatieven",
            "genre": "http://vocab.getty.edu/aat/300393160",
        },
        {
            "@id": "vlakfilms-kleur",
            "name": "Vlakfilms kleur",
            "genre": "http://vocab.getty.edu/aat/300127350",
        },
    ],
    "G": [
        {
            "@id": "glasnegatieven",
            "name": "Glasnegatieven",
            "genre": "http://vocab.getty.edu/aat/300393160",
        },
        {
            "@id": "rolfilms",
            "name": "6x9 rolfilms",
            "genre": "http://vocab.getty.edu/aat/300127382",
        },
    ],
    "L": [
        {
            "@id": "luchtfotos",
            "name": "Luchtfoto's",
            "genre": "http://vocab.getty.edu/aat/300128222",
        }
    ],
    "K": [
        {
            "@id": "kleinbeeld",
            "name": "Kleinbeeld",
            "genre": "http://vocab.getty.edu/aat/300263816",
        }
    ],
    "KC": [
        {
            "@id": "kleinbeeld",
            "name": "Kleinbeeld",
            "genre": "http://vocab.getty.edu/aat/300263816",
        }
    ],
    "A": [
        {
            "@id": "rolfilms",
            "name": "6x6 rolfilms",
            "genre": "http://vocab.getty.edu/aat/300127382",
        }
    ],
    "AC": [
        {
            "@id": "rolfilms-kleur",
            "name": "6x6 rolfilms kleur",
            "genre": "http://vocab.getty.edu/aat/300127382",
        }
    ],
}


location_type2concept = {
    "Adres": "https://vocab.getty.edu/aat/300386983",
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
    Columns:
        - uuid
        - Objectnummer
        - Omschrijving
        - Gepubliceerde foto
        - Expliciete foto
        - Geïmporteerd vanuit VH (Project 1)
        - Export naar VH (Project 2)
        - Geëxporteerd naar VH (Project 2)
        - Serienaam VH (Project 2)
        - OCR
        - OCR origineel
        - Aanbieden voor OCR
        - Naar krant-en-fotos.nl
        - Toon op web
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

    for n, row in df.iterrows():
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
                HANDLE.term("report/" + photo2reportuuid[row["uuid"]]),
            )

        # OCR
        # if not pd.isna(row["OCR"]):
        #     photo.add(SDO.text, Literal(row["OCR"]))

        # IIIF
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


def process_negatives(csv_path: str, g: Graph, g_reports: Graph):
    """

    Columns:
        - uuid
        - modified_time
        - Logboeknummer
        - Kaartnummer
        - Deelcollectie
        - Serienaam
        - metadata de Boer-metadata De Boer-uuid
    """

    df = pd.read_csv(
        csv_path,
        sep=";",
        encoding="utf-8",
        low_memory=False,
    )

    for _, row in df.iterrows():
        negative_number = row["Logboeknummer"] + row["Kaartnummer"]
        negative = Resource(g, HANDLE.term(negative_number))
        negative.add(RDF.type, SDO.CreativeWork)

        negative.add(SDO.identifier, Literal(negative_number))

        # Collection
        collection = Resource(g, HANDLE.term("collection/" + row["Deelcollectie"]))
        collection.add(RDF.type, SDO.Collection)
        collection.add(SDO.name, Literal(row["Deelcollectie"]))

        # Serie  #TODO
        series = Resource(
            g, HANDLE.term("series/" + row["Serienaam"].replace(" ", "").lower())
        )
        series.add(RDF.type, SDO.Collection)
        series.add(SDO.name, Literal(row["Serienaam"]))
        series.add(SDO.isPartOf, collection.identifier)

        negative.add(SDO.isPartOf, series)

        # Logboek
        logbook = Resource(g, HANDLE.term(row["Logboeknummer"]))
        logbook.add(RDF.type, SDO.CreativeWork)

        # Reports
        if not pd.isna(row["metadata de Boer-metadata De Boer-uuid"]):
            for i in row["metadata de Boer-metadata De Boer-uuid"].split("|"):
                g_reports.add(
                    (HANDLE.term("report/" + i), SDO.result, negative.identifier)
                )


def process_reports(csv_path: str, g: Graph):
    """

    Table: Metadata De Boer

    Columns:
        - uuid
        - modified_time
        - ordering
        - Invoernummer onderwerpskaarten
        - Beschrijving
        - Catalogus kaart scan
        - Datum
        - Logboek pagina ID
        - Invoernummer VH
        - Gemaakt in VeleHanden
        - Deelcollectie
        - Code

    Args:
        g (Graph): _description_
    """

    df = pd.read_csv(csv_path, sep=";", encoding="utf-8", low_memory=False)

    organization = Resource(g, URIRef("https://ror.org/03fsb6681"))  # ROR
    organization.add(RDF.type, SDO.ArchiveOrganization)
    organization.add(SDO.name, Literal("Noord-Hollands Archief"))
    organization.add(SDO.url, URIRef("https://noord-hollandsarchief.nl/"))

    collection = Resource(g, HANDLE.term("collection/FotopersbureauDeBoer"))
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
            deelcollectie = Resource(g, collection.identifier + "#" + value["@id"])
            deelcollectie.add(RDF.type, SDO.Collection)
            deelcollectie.add(RDF.type, SDO.ArchiveComponent)
            deelcollectie.add(SDO.name, Literal(value["name"], lang="nl"))
            deelcollectie.add(SDO.isPartOf, collection.identifier)
            deelcollectie.add(SDO.genre, URIRef(value["genre"]))

    for _, row in df.iterrows():
        report = Resource(g, HANDLE.term("report/" + row["uuid"]))
        report.add(RDF.type, SDO.CreativeWork)  # Collection?

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
                report.add(SDO.isPartOf, collection.identifier + "#" + i["@id"])

    # Catalogus kaart scan
    # Code

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
                    HANDLE.term("report/" + row["uuid"]),
                    SDO.about,
                    HANDLE.term("person/observation/" + i),
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
                    HANDLE.term("report/" + row["uuid"]),
                    SDO.about,
                    HANDLE.term("location/" + i),
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
            g.add((HANDLE.term("report/" + row["uuid"]), SDO.about, NHAT.term(i)))


def process_catalog_cards(csv_path: str, g: Graph):
    """

    Columns:
        - uuid
        - modified_time
        - ordering
        - Titel
        - Link NHA Thesaurus-identifier
        - Link NHA Thesaurus-term
        - Beschrijving
        - Bestandsnaam
        - Mapnaam
        - Export naar VH
        - Geëxporteerd naar VH
        - Onderwerpen
        - Verwijzingen
        - Beginjaar
        - Eindjaar
    """

    df = pd.read_csv(csv_path, sep=";", encoding="utf-8", low_memory=False)

    for _, row in df.iterrows():
        card = Resource(g, HANDLE.term("catalog/" + row["uuid"]))
        card.add(RDF.type, SDO.CreativeWork)

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


def process_locations(g: Graph):
    """
    Columns:
        - uuid
        - modified_time
        - ordering
        - Soort
        - Land
        - Gemeente
        - Plaats
        - Straat
        - Huisnummer
        - Huisletter
        - Huisnummertoevoeging
        - Postcode
        - Object
        - Wijk
        - Water
        - Regio
        - Park
        - Wegen
        - WikiData ID
        - WikiData URL
        - Wikipedia URL
        - BAG Pand ID
        - BAG Pand URL
        - BAG OpenbareRuimte ID
        - BAG OpenbareRuimte URL
        - BAG Nummeraanduiding ID
        - BAG Nummeraanduiding URL
        - Coordinates-uuid
        - Coordinates-modified_by-uuid
        - Coordinates-modified_by-username
        - Coordinates-modified_by-displayname
        - Coordinates-modified_by-email
        - Coordinates-modified_by-active
        - Coordinates-modified_by-admin
        - Coordinates-modified_time
        - Coordinates-ordering
        - Coordinates-address
        - Coordinates-lat
        - Coordinates-lng
        - Coordinates-zoom
        - Coordinates-wkt
        - Coordinates-geodata

    Args:
        g (Graph): _description_
    """
    for key, value in location_type2concept.items():
        concept = Resource(g, URIRef(value))
        concept.add(RDF.type, SKOS.Concept)
        concept.add(SKOS.prefLabel, Literal(key))

    df = pd.read_csv(
        "export/4_LocatiesMetCoordinaten20231213.csv",
        sep=";",
        encoding="utf-8",
        low_memory=False,
    )

    for _, row in df.iterrows():
        location = Resource(g, HANDLE.term("location/" + row["uuid"]))
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


def process_person_observations(g: Graph, g_reconstructions: Graph):
    """
    _summary_

    Columns:
        - uuid
        - modified_time
        - ordering
        - prefLabel
        - Label observatie
        - Type
        - Prefix (pnv:prefix)
        - Initialen (pnv:initials)
        - Voornaam (pnv:givenName)
        - Infix (pnv:infixTitle)
        - Tussenvoegsel (pnv:surnamePrefix)
        - Achternaam (pnv:baseSurname)
        - Patroniem (pnv:patronym)
        - Onderscheidend achtervoegsel (pnv:disambiguatingDescription)
        - Volledige naam (pnv:literalName)
        - Publiek persoon
        - Wikidata ID"

    Args:
        g (Graph): _description_
    """

    df = pd.read_csv(
        "export/5_PersoonObservaties20231128.csv",
        sep=";",
        encoding="utf-8",
        low_memory=False,
    )
    for _, row in df.iterrows():
        person = Resource(g, HANDLE.term("person/observation/" + row["uuid"]))
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

    # Reconstructions
    df = pd.read_csv(
        "export/5_UUIDPersoonObsMetRec20231128.csv",
        sep=";",
        encoding="utf-8",
        low_memory=False,
    )
    for _, row in df.iterrows():
        if pd.isna(row["Persoon reconstructie-uuid"]):
            continue
        for i in row["Persoon reconstructie-uuid"].split("|"):
            g_reconstructions.add(
                (
                    HANDLE.term(
                        "person/reconstruction/" + row["Persoon reconstructie-uuid"]
                    ),
                    PROV.wasDerivedFrom,
                    HANDLE.term("person/observation/" + row["uuid"]),
                )
            )


def process_person_reconstructions(g: Graph):
    """
    Columns:
    - uuid
    - modified_time
    - ordering
    - Label
    - Type
    - Prefix (pnv:prefix)
    - Initialen (pnv:initials)
    - Voornaam (pnv:givenName)
    - Infix (pnv:infixTitle)
    - Tussenvoegsel (pnv:surnamePrefix)
    - Achternaam (pnv:baseSurname)
    - Patroniem (pnv:patronym)
    - Onderscheidend achtervoegsel (pnv:disambiguatingDescription)
    - Volledige naam (pnv:literalName)
    - Beschrijving
    - Geboortedatum
    - Geboorteplaats
    - Overlijdensdatum
    - Overlijdensplaats
    - Beroep
    - Publiek persoon
    - Wikidata ID
    - Wikidata URI
    - Wikipedia URL

    Args:
        g (Graph): _description_
    """

    df = pd.read_csv(
        "export/6_PersoonReconstructies20231128.csv",
        sep=";",
        encoding="utf-8",
        low_memory=False,
    )
    for _, row in df.iterrows():
        person = Resource(g, HANDLE.term("person/reconstruction/" + row["uuid"]))
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


def process_gtaa(g: Graph, mapping_file):
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
    g_identifier = HANDLE.term("photos/")
    print("Processing photos...")
    process_photos("export/0_Reportagefotos20231128.csv", g_identifier, split_by=50_000)

    # # 1. Negatiefvellen
    # g = ds.graph(identifier=HANDLE.term("negatives/"))
    # g_reports = ds.graph(identifier=HANDLE.term("reports/"))
    # print("Processing negatives...")
    # process_negatives(
    #     "export/1_NegatiefvellenAndUUIDMetadata20231211.csv", g, g_reports
    # )

    # 2. Metadata De Boer (reportages)
    g = ds.graph(identifier=HANDLE.term("reports/"))
    print("Processing reports...")
    process_reports("export/2_MetadataDeBoer20231128.csv", g)

    # 3. Cataloguskaarten
    g = ds.graph(identifier=HANDLE.term("catalogs/"))
    print("Processing catalog cards...")
    process_catalog_cards("export/3_Cataloguskaarten20231128.csv", g)

    # 4. Locaties
    g = ds.graph(identifier=HANDLE.term("locations/"))
    print("Processing locations...")
    process_locations(g)

    # 5. Personen (observaties)
    g = ds.graph(identifier=HANDLE.term("persons/observations/"))
    g_reconstructions = ds.graph(identifier=HANDLE.term("persons/reconstructions/"))
    print("Processing person observations...")
    process_person_observations(g, g_reconstructions)

    # 6. Personen (reconstructies)
    g = ds.graph(identifier=HANDLE.term("persons/reconstructions/"))
    print("Processing person reconstructions...")
    process_person_reconstructions(g)

    # 8. GTAA
    g = ds.graph(identifier=HANDLE.term("reports/"))  # same graph as reports
    print("Processing gtaa...")
    process_gtaa(g, "scripts/wd2gtaa.json")

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
    ds.bind("report", HANDLE.term("report/"))
    ds.bind("catalog", HANDLE.term("catalog/"))
    ds.bind("location", HANDLE.term("location/"))
    ds.bind("personobservation", HANDLE.term("person/observation/"))
    ds.bind("personreconstruction", HANDLE.term("person/reconstruction/"))
    ds.bind("subject", HANDLE.term("subject/"))
    ds.bind("gtaa", GTAA)
    ds.bind("geo", GEO)
    ds.bind("aat", AAT)

    print()
    print("Serializing...")

    for g in ds.graphs():
        if str(g.identifier) == "urn:x-rdflib:default":
            continue
        name = g.identifier.split(HANDLE.term(""))[1].replace("/", "")

        print(f"Serializing {name}...")
        g.serialize(f"nha_{name}.trig", format="trig")


if __name__ == "__main__":
    main()
