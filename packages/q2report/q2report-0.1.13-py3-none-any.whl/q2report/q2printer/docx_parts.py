docx_parts={}
docx_parts['doc_start'] = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document 
    xmlns:wne="http://schemas.microsoft.com/office/word/2006/wordml" 
    xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" 
    xmlns:w10="urn:schemas-microsoft-com:office:word" 
    xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" 
    xmlns:v="urn:schemas-microsoft-com:vml" 
    xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" 
    xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" 
    xmlns:o="urn:schemas-microsoft-com:office:office" 
    xmlns:ve="http://schemas.openxmlformats.org/markup-compatibility/2006">
<w:body>

"""
docx_parts['image'] = """
    <w:drawing>
        <wp:anchor distT="0" distB="0" distL="0" distR="0" simplePos="0" relativeHeight="0" behindDoc="1" locked="0" 
                        layoutInCell="0" allowOverlap="1">
            <wp:simplePos x="0" y="0"/>
            <wp:positionH relativeFrom="column">
                <wp:posOffset>%s</wp:posOffset> 
            </wp:positionH>
            <wp:positionV relativeFrom="paragraph">
                <wp:posOffset>0</wp:posOffset>
            </wp:positionV>
            <wp:extent cx="%s" cy="%s"/>
            <wp:effectExtent l="0" t="0" r="0" b="0"/>
            <wp:wrapNone/>
            <wp:docPr id="%s" name="Picture %s"/>
            <wp:cNvGraphicFramePr>
                <a:graphicFrameLocks xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"/>
            </wp:cNvGraphicFramePr>
            <a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
                <a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">
                    <pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">
                        <pic:nvPicPr>
                            <pic:cNvPr id="0" name="Picture %s"/>
                            <pic:cNvPicPr preferRelativeResize="0">
                                <a:picLocks noChangeArrowheads="1"/>
                            </pic:cNvPicPr>
                        </pic:nvPicPr>
                        <pic:blipFill>
                            <a:blip r:embed="rId0"/><a:srcRect/>
                            <a:stretch>
                                <a:fillRect/>
                            </a:stretch>
                        </pic:blipFill>
                        <pic:spPr bwMode="auto">
                            <a:xfrm><a:off x="0" y="0"/>
                                <a:ext cx="%s" cy="%s"/>
                            </a:xfrm>
                            <a:prstGeom prst="rect">
                                <a:avLst/>
                            </a:prstGeom>
                        </pic:spPr>
                    </pic:pic>
                </a:graphicData>
            </a:graphic>
        </wp:anchor>
    </w:drawing>"""
docx_parts['rels'] = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    <Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
    <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
    </Relationships>"""
docx_parts['content_type'] = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    <Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
    <Default Extension="jpg" ContentType="image/jpg"/>
    <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
    <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
    </Types>"""
docx_parts['word_rels'] = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    <Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
    %s
    </Relationships>"""
docx_parts['images'] = """<Relationship Id="rId%s" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" 
    Target="media/image%s.jpg"/>"""
