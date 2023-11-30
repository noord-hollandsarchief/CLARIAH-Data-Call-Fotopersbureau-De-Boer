import json
from collections import defaultdict

from rdflib import (
    Graph,
    Namespace,
    Literal,
    URIRef,
    RDF,
    RDFS,
    XSD,
    SDO,
    OWL,
    PROV,
    BNode,
)
from rdflib.resource import Resource

# from rdflib.collection import Collection
from rdflib.container import Seq

import pandas as pd

HANDLE = Namespace("https://hdl.handle.net/21.12102/")
RANH = Namespace("https://maior-images.memorix.nl/ranh/iiif/")
PNV = Namespace("https://w3id.org/pnv#")
WD = Namespace("http://www.wikidata.org/entity/")
GTAA = Namespace("http://data.beeldengeluid.nl/gtaa/")


def process_photos(csv_path: str, g: Graph):
    """


    Columns:
        - uuid
        - modified_by-uuid
        - modified_by-username
        - modified_by-displayname
        - modified_by-email
        - modified_by-active
        - modified_by-admin
        - modified_time
        - Objectnummer
        - Twijfel metadata
        - Omschrijving
        - Gepubliceerde foto
        - Expliciete foto
        - Geïmporteerd vanuit VH (Project 1)
        - Export naar VH (Project 2)
        - Geëxporteerd naar VH (Project 2)
        - Serienaam VH (Project 2)
        - OCR *
        - OCR origineel
        - Aanbieden voor OCR
        - Naar krant-en-fotos.nl
        - Toon op web
        # - file-count
        # - thumbnail
        # - t2_serie_name
        # - t3_description
        # - t3_entry_number
        # - t3_log_page_id
        # - t3_vh_entry_number
        # - t3_catalog_card
        # - vh_keywords_title
        # - vh_keywords_correct
        # - ai_keywords_title
        # - t6_link
        # - t6_link_thumbnail
        # - t6_photo_id
        # - t6_paper_id
        # - t6_score
        # - t6_match


    Args:
        g (Graph): rdflib graph object
    """
    negative2photo = defaultdict(dict)

    df = pd.read_csv(csv_path, sep=";", encoding="utf-8")

    for n, row in df.iterrows():
        if pd.isna(row["Objectnummer"]) or "test" in row["Objectnummer"]:
            continue

        photo = Resource(g, HANDLE.term(row["uuid"]))
        photo.add(RDF.type, SDO.Photograph)
        photo.add(SDO.identifier, Literal(row["Objectnummer"]))

        # Report
        negative_number, photo_number = row["Objectnummer"].rsplit("_", 1)  # TODO
        if "]" in negative_number:
            negative_number = negative_number.replace("]", "")  # TODO
        if negative_number:
            photo.add(SDO.isPartOf, HANDLE.term(negative_number))

            negative2photo[negative_number][photo_number] = photo.identifier

    # IIIF
    df = pd.read_csv(
        "export/ReportageFotosAssetUUIDs20231128.csv", sep=";", encoding="utf-8"
    )
    for _, row in df.iterrows():
        full_image_uri = RANH.term(
            row["Linked media-uuid"] + "/full/full/0/default.jpg"
        )
        thumb_image_uri = RANH.term(
            row["Linked media-uuid"] + "/full/,250/0/default.jpg"
        )
        image = Resource(g, RANH.term(row["Linked media-uuid"]))
        image.add(RDF.type, SDO.ImageObject)
        image.add(SDO.contentUrl, full_image_uri)
        image.add(SDO.thumbnailUrl, thumb_image_uri)
        image.add(SDO.name, Literal(row["Linked media-name"]))

        g.add((HANDLE.term(row["uuid"]), SDO.image, image.identifier))

        # OCR
        # photo.add(SDO.text, Literal(row["OCR"]))
        # process_photo_OCR(g, row["OCR_origineel"], photo) #TODO

        # Krant en foto
        # process_photo_keywords(g, row["ai_keywords_title"], photo)

        # HisVis keywords

        # if n == 100:
        #     break

    for k, v in negative2photo.items():
        negative2photo[k] = dict(sorted(v.items()))

    return negative2photo


def process_negatives(csv_path: str, g: Graph, negative2photo: dict = {}):
    """

    Columns:
    - uuid
    - modified_time
    - ordering
    - Logboeknummer
    - Kaartnummer
    - Deelcollectie
    - Serienummer
    - Serienaam
    - Voorkeur
    - metadata de Boer-uuid
    - metadata de Boer-metadata De Boer-uuid
    - Export naar VH
    - Geëxporteerd naar VH"

    """

    df = pd.read_csv(
        csv_path,
        sep=";",
        encoding="utf-8",
    )

    for _, row in df.iterrows():
        negative_number = row["Logboeknummer"] + row["Kaartnummer"]
        negative = Resource(g, HANDLE.term(negative_number))
        negative.add(RDF.type, SDO.CreativeWork)

        negative.add(SDO.identifier, Literal(negative_number))

        # Serie
        series = Resource(g, HANDLE.term(row["Serienummer"]))
        series.add(RDF.type, SDO.Collection)
        series.add(SDO.name, Literal(row["Serienaam"]))
        series.add(SDO.isPartOf, HANDLE.term(row["Deelcollectie"]))  # TODO

        negative.add(SDO.isPartOf, series)

        # Logboek
        logbook = Resource(g, HANDLE.term(row["Logboeknummer"]))
        logbook.add(RDF.type, SDO.CreativeWork)

        # Reports
        if not pd.isna(row["metadata de Boer-metadata De Boer-uuid"]):
            for i in row["metadata de Boer-metadata De Boer-uuid"].split("|"):
                g.add((HANDLE.term("report/" + i), SDO.result, negative.identifier))

        # Photos
        if negative_number in negative2photo:
            seq = Seq(g, BNode(), list(negative2photo[negative_number].values()))
            negative.add(SDO.hasPart, seq.uri)


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

    df = pd.read_csv(csv_path, sep=";", encoding="utf-8")

    for _, row in df.iterrows():
        report = Resource(g, HANDLE.term("report/" + row["uuid"]))
        report.add(RDF.type, SDO.CreativeWork)  # Collection?

        if not pd.isna(row["Invoernummer onderwerpskaarten"]):
            for i in row["Invoernummer onderwerpskaarten"].split("|"):
                report.add(SDO.identifier, Literal(i))

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

        report.add(SDO.isPartOf, Literal(row["Deelcollectie"]))  # TODO

    # Catalogus kaart scan
    # Code

    ## Persons
    df = pd.read_csv(
        "export/UUIDMetadataMetPersonenObs20231128.csv", sep=";", encoding="utf-8"
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
        "export/UUIDMetadataMetLocaties20231128.csv", sep=";", encoding="utf-8"
    )

    for _, row in df.iterrows():
        if pd.isna(row["Locaties-uuid"]):
            continue
        for i in row["Locaties-uuid"].split("|"):
            g.add(
                (
                    HANDLE.term("report/" + row["uuid"]),
                    SDO.about,
                    HANDLE.term("location/" + i),
                )
            )

    ## Subjects
    # df = pd.read_csv(
    #     "export/UUIDMetadataMetCataloguskaart20231128.csv", sep=";", encoding="utf-8"
    # )
    # for _, row in df.iterrows():
    #     if pd.isna(row["Catalogus kaart-uuid"]):
    #         continue
    #     for i in row["Catalogus kaart-uuid"].split("|"):
    #         g.add(
    #             (
    #                 HANDLE.term("report/" + row["uuid"]),
    #                 SDO.about,
    #                 HANDLE.term("subject/" + i),
    #             )
    #         )


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

    df = pd.read_csv(csv_path, sep=";", encoding="utf-8")

    for _, row in df.iterrows():
        card = Resource(g, HANDLE.term("catalog/" + row["uuid"]))
        card.add(RDF.type, SDO.CreativeWork)

        card.add(SDO.name, Literal(row["Titel"]))
        card.add(SDO.temporalCoverage, Literal(f"{row['Beginjaar']}/{row['Eindjaar']}"))

        # Link NHA Thesaurus-identifier
        pp_uri = URIRef(row["Link NHA Thesaurus-identifier"].split(":")[1])
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
        - Coordinates-modified_time
        - Coordinates-ordering
        - Coordinates-address
        - Coordinates-lat
        - Coordinates-lng
        - Coordinates-zoom
        - Coordinates-wkt
        - Coordinates-geodata"


    Args:
        g (Graph): _description_
    """

    df = pd.read_csv("export/4_Locaties20231128.csv", sep=";", encoding="utf-8")

    for _, row in df.iterrows():
        location = Resource(g, HANDLE.term("location/" + row["uuid"]))
        location.add(RDF.type, SDO.Place)

        # "Land";"Gemeente";"Plaats";"Straat";"Huisnummer";"Huisletter";"Huisnummertoevoeging";"Postcode";"Object";"Wijk";"Water";"Regio";"Park";"Wegen"

        name = None
        for i in [
            row["Wegen"],
            row["Park"],
            row["Regio"],
            row["Water"],
            row["Wijk"],
            row["Object"],
            row["Postcode"],
            row["Huisnummertoevoeging"],
            row["Huisletter"],
            row["Huisnummer"],
            row["Straat"],
            row["Plaats"],
            row["Gemeente"],
            row["Land"],
        ]:
            if not pd.isna(i):
                name = i
                break

        if name:
            location.add(SDO.name, Literal(name))

        if not pd.isna(row["WikiData ID"]):
            location.add(OWL.sameAs, WD.term(row["WikiData ID"]))


def process_person_observations(g: Graph):
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
        "export/5_PersoonObservaties20231128.csv", sep=";", encoding="utf-8"
    )
    for _, row in df.iterrows():
        person = Resource(g, HANDLE.term("person/observation/" + row["uuid"]))
        person.add(RDF.type, SDO.Person)
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
        "export/UUIDPersoonObsMetRec20231128.csv", sep=";", encoding="utf-8"
    )
    for _, row in df.iterrows():
        if pd.isna(row["Persoon reconstructie-uuid"]):
            continue
        for i in row["Persoon reconstructie-uuid"].split("|"):
            g.add(
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
        "export/6_PersoonReconstructies20231128.csv", sep=";", encoding="utf-8"
    )
    for _, row in df.iterrows():
        person = Resource(g, HANDLE.term("person/reconstruction/" + row["uuid"]))
        person.add(RDF.type, SDO.Person)
        person.add(SDO.name, Literal(row["Label"]))

        if not pd.isna(row["Beschrijving"]):
            person.add(SDO.description, Literal(row["Beschrijving"]))

        if not pd.isna(row["Geboortedatum"]):
            person.add(SDO.birthDate, Literal(row["Geboortedatum"]))

        if not pd.isna(row["Geboorteplaats"]):
            person.add(SDO.birthPlace, Literal(row["Geboorteplaats"]))

        if not pd.isna(row["Overlijdensdatum"]):
            person.add(SDO.deathDate, Literal(row["Overlijdensdatum"]))

        if not pd.isna(row["Overlijdensplaats"]):
            person.add(SDO.deathPlace, Literal(row["Overlijdensplaats"]))

        if not pd.isna(row["Beroep"]):
            person.add(SDO.hasOccupation, Literal(row["Beroep"]))

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


def process_hisvis(g: Graph):
    df = pd.read_csv("export/7_AiTrefwoorden20231128", sep=";", encoding="utf-8")

    for _, row in df.iterrows():
        # concept = SKOS.Concept(HANDLE.term(row["uuid"]))
        pass


def process_gtaa(g: Graph, mapping_file):
    with open(mapping_file) as f:
        mapping = json.load(f)

    for wd_id, gtaa_ids in mapping.items():
        for i in gtaa_ids:
            g.add((WD.term(wd_id), OWL.sameAs, GTAA.term(i)))


def main():
    g = Graph()

    # 0. Foto's
    negative2photo = process_photos("export/0_Reportagefotos20231128.csv", g)

    # 1. Negatiefvellen
    process_negatives(
        "export/1_Negatiefvellen20231128_inclUUIDMetadataDeBoer.csv",
        g,
        negative2photo=negative2photo,
    )

    # 2. Metadata De Boer (rapportages)
    process_reports("export/2_MetadataDeBoer20231128.csv", g)

    # 3. Cataloguskaarten
    process_catalog_cards("export/3_Cataloguskaarten20231128.csv", g)

    # 4. Locaties
    process_locations(g)

    # 5. Personen (observaties)

    process_person_observations(g)

    # 6. Personen (reconstructies)

    process_person_reconstructions(g)

    # 7. AI-trefwoorden
    # process_hisvis(g)

    # 8. GTAA
    process_gtaa(g, "scripts/wd2gtaa.json")

    g.bind("pnv", PNV)
    g.bind("wd", WD)
    g.bind("owl", OWL)
    g.bind("schema", SDO)
    g.bind("prov", PROV)

    g.bind("nha", HANDLE)
    g.bind("report", HANDLE.term("report/"))
    g.bind("catalog", HANDLE.term("catalog/"))
    g.bind("location", HANDLE.term("location/"))
    g.bind("personobservation", HANDLE.term("person/observation/"))
    g.bind("personreconstruction", HANDLE.term("person/reconstruction/"))
    g.bind("subject", HANDLE.term("subject/"))

    g.bind("gtaa", GTAA)

    print("Serializing...")
    g.serialize("nha_deboer.trig", format="trig")


if __name__ == "__main__":
    main()
