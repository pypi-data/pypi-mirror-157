"""Module for a list of MediaFileLink objects."""
from open_publishing.core import DatabaseObjectsList
from open_publishing.core.enums import MediaFileTypeCode, PublicationType

from .mediafile_link import MediaFileLink

class MediafileLinkList(DatabaseObjectsList):
    """Class for a list of MediaFileLink objects."""
    _database_object_type = MediaFileLink

    def __init__(self,
                 document):
        """Initialize list of MediaFileLink objects."""
        super(MediafileLinkList, self).__init__(
            database_object=document,
            aspect='mediafile_links',
            list_locator='mediafile_links')
        self._document = document

    def add(self,
            url,
            type_code,
            publication_type):
        if type_code not in MediaFileTypeCode:
            raise TypeError('type_code should be one of op.mediafile.type_code.*')
        if publication_type not in PublicationType:
            raise TypeError('type_code should be one of op.publication.*')
        res = self._database_object._context.gjp.create(MediaFileLink._object_class,
                                                        media_file_link=url,
                                                        media_file_type_code=type_code.identifier,
                                                        publication_type=publication_type.identifier,
                                                        document_id=self._document.document_id)


        mediafile_link_id = MediaFileLink.id_from_guid(res["GUID"])
        self._objects[mediafile_link_id] = MediaFileLink(context = self._document._context,
                                                         mediafile_link_id = mediafile_link_id)

        self._ids.append(mediafile_link_id)

        
