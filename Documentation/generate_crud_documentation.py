from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZIP_DEFLATED, ZipFile


OUTPUT_FILE = Path(__file__).with_name("CRUD_Testing_Documentation.docx")

WORD_NAMESPACE = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
RELATIONSHIP_NAMESPACE = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PACKAGE_RELATIONSHIP_NAMESPACE = "http://schemas.openxmlformats.org/package/2006/relationships"
CONTENT_TYPES_NAMESPACE = "http://schemas.openxmlformats.org/package/2006/content-types"

ET.register_namespace("w", WORD_NAMESPACE)
ET.register_namespace("r", RELATIONSHIP_NAMESPACE)
ET.register_namespace("", PACKAGE_RELATIONSHIP_NAMESPACE)


def word_tag(name):
    return f"{{{WORD_NAMESPACE}}}{name}"


def add_paragraph(parent, text="", style=None, bold=False):
    paragraph = ET.SubElement(parent, word_tag("p"))
    if style:
        properties = ET.SubElement(paragraph, word_tag("pPr"))
        ET.SubElement(properties, word_tag("pStyle"), {word_tag("val"): style})

    run = ET.SubElement(paragraph, word_tag("r"))
    if bold:
        run_properties = ET.SubElement(run, word_tag("rPr"))
        ET.SubElement(run_properties, word_tag("b"))
    text_element = ET.SubElement(run, word_tag("t"))
    text_element.text = text
    return paragraph


def build_document():
    document = ET.Element(word_tag("document"))
    body = ET.SubElement(document, word_tag("body"))

    add_paragraph(body, "Django CRUD Testing", style="Title")
    add_paragraph(
        body,
        "Documentation for the automated tests of the Blog article CRUD functionality.",
    )

    add_paragraph(body, "Project overview", style="Heading1")
    add_paragraph(
        body,
        "The Django blog application stores articles in the Blog model. "
        "Each article has a title, content, optional image filename, and view count.",
    )
    add_paragraph(
        body,
        "CRUD means Create, Read, Update, and Delete. The tests use Django's "
        "TestCase client to send requests to the application without starting a server.",
    )

    add_paragraph(body, "Test file", style="Heading1")
    add_paragraph(
        body,
        "The CRUD tests are in django_blog/blog/test_crud.py, in the "
        "BlogCRUDTests test case.",
    )

    add_paragraph(body, "Scenarios covered", style="Heading1")
    scenarios = [
        ("Create - form display", "GET blog:create returns HTTP 200 and the article form."),
        (
            "Create - valid submission",
            "POST with valid article data creates a Blog record and redirects to its detail page.",
        ),
        (
            "Create - invalid submission",
            "POST without a required title redisplays the form and does not create an empty-title article.",
        ),
        (
            "Update - form display",
            "GET blog:update/<id> returns the edit form bound to the selected article.",
        ),
        (
            "Update - valid submission",
            "POST with updated data saves the title, content, and image, then redirects to the detail page.",
        ),
        (
            "Delete - confirmation page",
            "GET blog:delete/<id> displays the confirmation page and keeps the article.",
        ),
        (
            "Delete - confirmed submission",
            "POST blog:delete/<id> removes the article and redirects to the article list.",
        ),
    ]
    for name, description in scenarios:
        add_paragraph(body, name, style="Heading2")
        add_paragraph(body, description)

    add_paragraph(body, "How to run the tests", style="Heading1")
    add_paragraph(body, "Open a terminal in the django_blog project directory and run:")
    add_paragraph(body, "python manage.py test blog", style="Code")
    add_paragraph(
        body,
        "Django creates a temporary test database, runs the test cases, and removes "
        "the database when the test run finishes. A successful run reports OK.",
    )

    add_paragraph(body, "Assertions", style="Heading1")
    assertions = [
        "HTTP response status codes and redirects are correct.",
        "Expected Django templates are rendered.",
        "Valid form submissions persist the expected model values.",
        "Invalid submissions do not create an article.",
        "GET requests for deletion do not remove data; confirmed POST requests do.",
    ]
    for assertion in assertions:
        add_paragraph(body, assertion, style="ListParagraph")

    section_properties = ET.SubElement(body, word_tag("sectPr"))
    ET.SubElement(
        section_properties,
        word_tag("pgSz"),
        {word_tag("w"): "12240", word_tag("h"): "15840"},
    )
    ET.SubElement(
        section_properties,
        word_tag("pgMar"),
        {
            word_tag("top"): "1440",
            word_tag("right"): "1440",
            word_tag("bottom"): "1440",
            word_tag("left"): "1440",
        },
    )
    return ET.tostring(document, encoding="utf-8", xml_declaration=True)


def build_styles():
    styles = ET.Element(word_tag("styles"))
    definitions = [
        ("Normal", "Normal", "Calibri", "22"),
        ("Title", "Title", "Calibri", "36"),
        ("Heading1", "heading 1", "Calibri", "30"),
        ("Heading2", "heading 2", "Calibri", "24"),
        ("Code", "Normal", "Consolas", "20"),
        ("ListParagraph", "Normal", "Calibri", "22"),
    ]
    for style_id, name, font, size in definitions:
        style = ET.SubElement(
            styles,
            word_tag("style"),
            {word_tag("type"): "paragraph", word_tag("styleId"): style_id},
        )
        ET.SubElement(style, word_tag("name"), {word_tag("val"): name})
        if style_id != "Normal":
            ET.SubElement(style, word_tag("basedOn"), {word_tag("val"): "Normal"})
        run_properties = ET.SubElement(style, word_tag("rPr"))
        ET.SubElement(run_properties, word_tag("rFonts"), {word_tag("ascii"): font})
        ET.SubElement(run_properties, word_tag("sz"), {word_tag("val"): size})
        if style_id in ("Title", "Heading1", "Heading2"):
            ET.SubElement(run_properties, word_tag("b"))
    return ET.tostring(styles, encoding="utf-8", xml_declaration=True)


def create_word_document():
    content_types = ET.Element(
        f"{{{CONTENT_TYPES_NAMESPACE}}}Types",
    )
    ET.SubElement(
        content_types,
        f"{{{CONTENT_TYPES_NAMESPACE}}}Default",
        {"Extension": "rels", "ContentType": "application/vnd.openxmlformats-package.relationships+xml"},
    )
    ET.SubElement(
        content_types,
        f"{{{CONTENT_TYPES_NAMESPACE}}}Default",
        {"Extension": "xml", "ContentType": "application/xml"},
    )
    ET.SubElement(
        content_types,
        f"{{{CONTENT_TYPES_NAMESPACE}}}Override",
        {
            "PartName": "/word/document.xml",
            "ContentType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml",
        },
    )
    ET.SubElement(
        content_types,
        f"{{{CONTENT_TYPES_NAMESPACE}}}Override",
        {
            "PartName": "/word/styles.xml",
            "ContentType": "application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml",
        },
    )

    package_relationships = ET.Element(
        f"{{{PACKAGE_RELATIONSHIP_NAMESPACE}}}Relationships",
    )
    ET.SubElement(
        package_relationships,
        f"{{{PACKAGE_RELATIONSHIP_NAMESPACE}}}Relationship",
        {
            "Id": "rId1",
            "Type": "http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument",
            "Target": "word/document.xml",
        },
    )

    document_relationships = ET.Element(
        f"{{{PACKAGE_RELATIONSHIP_NAMESPACE}}}Relationships",
    )
    ET.SubElement(
        document_relationships,
        f"{{{PACKAGE_RELATIONSHIP_NAMESPACE}}}Relationship",
        {
            "Id": "rId1",
            "Type": "http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles",
            "Target": "styles.xml",
        },
    )

    with ZipFile(OUTPUT_FILE, "w", ZIP_DEFLATED) as word_file:
        word_file.writestr(
            "[Content_Types].xml",
            ET.tostring(content_types, encoding="utf-8", xml_declaration=True),
        )
        word_file.writestr(
            "_rels/.rels",
            ET.tostring(package_relationships, encoding="utf-8", xml_declaration=True),
        )
        word_file.writestr(
            "word/document.xml",
            build_document(),
        )
        word_file.writestr(
            "word/styles.xml",
            build_styles(),
        )
        word_file.writestr(
            "word/_rels/document.xml.rels",
            ET.tostring(document_relationships, encoding="utf-8", xml_declaration=True),
        )

    print(f"Word documentation created: {OUTPUT_FILE}")


if __name__ == "__main__":
    create_word_document()
