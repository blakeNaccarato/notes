# generated by datamodel-codegen:
#   filename:  <stdin>
#   timestamp: 2023-02-10T16:53:31+00:00

# flake8: noqa: A003

from __future__ import annotations

from pydantic.v1 import BaseModel, Field


class Accessed(BaseModel):
    date_parts: list[list[int]] = Field(..., alias="date-parts")


class AuthorItem(BaseModel):
    family: str | None = None
    given: str | None = None
    literal: str | None = None


class Issued(BaseModel):
    date_parts: list[list[int]] = Field(..., alias="date-parts")


class DirectorItem(BaseModel):
    literal: str


class EditorItem(BaseModel):
    family: str
    given: str


class CollectionEditorItem(BaseModel):
    family: str
    given: str


class Submitted(BaseModel):
    date_parts: list[list[int | str]] = Field(..., alias="date-parts")


class ModelItem(BaseModel):
    id: str
    abstract: str | None = None
    accessed: Accessed | None = None
    author: list[AuthorItem] | None = None
    citation_key: str = Field(..., alias="citation-key")
    container_title: str | None = Field(None, alias="container-title")
    DOI: str | None = None
    issued: Issued | None = None
    language: str | None = None
    license: str | None = None
    page: str | None = None
    publisher: str | None = None
    section: str | None = None
    source: str | None = None
    title: str
    title_short: str | None = Field(None, alias="title-short")
    type: str
    URL: str | None = None
    ISBN: str | None = None
    number_of_pages: str | None = Field(None, alias="number-of-pages")
    container_title_short: str | None = Field(None, alias="container-title-short")
    ISSN: str | None = None
    issue: str | None = None
    volume: str | None = None
    number: str | None = None
    note: str | None = None
    dimensions: str | None = None
    director: list[DirectorItem] | None = None
    PMID: str | None = None
    collection_title: str | None = Field(None, alias="collection-title")
    editor: list[EditorItem] | None = None
    event_place: str | None = Field(None, alias="event-place")
    publisher_place: str | None = Field(None, alias="publisher-place")
    edition: str | None = None
    collection_editor: list[CollectionEditorItem] | None = Field(
        None, alias="collection-editor"
    )
    event_title: str | None = Field(None, alias="event-title")
    genre: str | None = None
    PMCID: str | None = None
    authority: str | None = None
    call_number: str | None = Field(None, alias="call-number")
    submitted: Submitted | None = None


class Model(BaseModel):
    __root__: list[ModelItem]
