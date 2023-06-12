import pandas as pd
import numpy as np

from rdflib import ConjunctiveGraph, Namespace, URIRef, Literal, RDF, SKOS, FOAF
from rdflib.resource import Resource

NHAF = Namespace("https://digitaalerfgoed.poolparty.biz/nhaf/")
TOPCONCEPT = NHAF.term("11aa07a8-4ed7-4ae0-9e1d-457c907b7f33")


def main():
    """
    uuid,ordering,Trefwoord,Titel,Beschrijving,Trefwoord (en),Titel (en),Beschrijving (en),Afbeelding,spacer,Afbeelding url,Linked media-uuid,Linked media-name,Linked media-folder,Linked media-filesize,Linked media-mimetype,Record notes-uuid,Record notes-modified_by-uuid,Record notes-modified_by-username,Record notes-modified_by-displayname,Record notes-modified_by-email,Record notes-modified_by-active,Record notes-modified_by-admin,Record notes-modified_time,Record notes-veldnaam,Record notes-notes
    0199e8d2-824a-b19a-be6a-5ee3beb624b5,,bos_park,Bos park,Foto's waarin een bos- en/of parklandschap / natuurgebied centraal staat,forest_park,Forest park,Picture taken in a forest or park,NL-HlmNHA_1478_4842.jpg,,https://images.memorix.nl/ranh/thumb/500x500/e6499640-e8ec-4855-b222-21e7d9d25e28.jpg,e6499640-e8ec-4855-b222-21e7d9d25e28,NL-HlmNHA_1478_4842,62730a48-682e-b290-69d7-b86d8c03669c,72452,image/jp2,,,,,,,,,,

    """

    df = pd.read_csv("scene_detection/SceneDetection20230510_UTF8.csv")
    df = df.replace({np.nan: None})

    g = ConjunctiveGraph()

    for d in df.to_dict(orient="records"):
        concept = Resource(g, NHAF.term(d["uuid"]))
        concept.add(RDF.type, SKOS.Concept)

        # Label
        if d["Titel"]:
            concept.add(SKOS.prefLabel, Literal(d["Titel"], lang="nl"))

        if d["Titel (en)"]:
            concept.add(SKOS.prefLabel, Literal(d["Titel (en)"], lang="en"))

        # Definition
        if d["Beschrijving"]:
            concept.add(SKOS.definition, Literal(d["Beschrijving"], lang="nl"))

        if d["Beschrijving (en)"]:
            concept.add(SKOS.definition, Literal(d["Beschrijving (en)"], lang="en"))

        # Depiction
        if d["Afbeelding url"]:
            concept.add(FOAF.depiction, URIRef(d["Afbeelding url"]))

        # PoolParty stuff
        concept.add(SKOS.broader, TOPCONCEPT)
        g.add((TOPCONCEPT, SKOS.narrower, concept.identifier))  # inverse

    g.serialize("scene_detection/SceneDetection20230510_UTF8.ttl", format="turtle")


if __name__ == "__main__":
    main()
