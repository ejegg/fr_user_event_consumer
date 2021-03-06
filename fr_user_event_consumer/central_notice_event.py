import re
import json
import logging
from datetime import datetime

from fr_user_event_consumer import db

EVENT_TIMESTAMP_FORMAT = '%Y-%m-%dT%H:%M:%SZ' # Coordinate with EventLogging
validate_banner_pattern = re.compile( '^[A-Za-z0-9_]+$' ) # Coordinate with CentralNotice

logger = logging.getLogger( __name__ )

class CentralNoticeEvent:

    def __init__( self, json_string ):
        self._raw_json = json_string

        # Validate event data
        self.valid = False

        try:
            self._data = json.loads( json_string )
        except ValueError as e:
            logger.debug( f'Invalid Json: {e}' )
            return

        try:
            self.country = db.country_mapper.get_or_new(
                self._data[ 'event' ][ 'country' ] )
        except ValueError as e:
            logger.debug( f'Invalid country: {e}' )
            return

        try:
            self.language = db.language_mapper.get_or_new(
                self._data[ 'event' ][ 'uselang' ] )
        except ValueError as e:
            logger.debug( f'Invalid language: {e}' )
            return

        try:
            self.project = db.project_mapper.get_or_new(
                self._data[ 'event' ][ 'project' ] )
        except ValueError as e:
            logger.debug( f'Invalid project: {e}' )
            return

        if 'banner' in self._data[ 'event' ]:
            self._banner = self._data[ 'event' ][ 'banner' ]
            if not validate_banner_pattern.match( self._banner ):
                logger.debug( f'Invalid banner: {self._banner}' )
                return
        else:
            self._banner = None

        try:
            self.time = datetime.strptime( self._data[ 'dt' ], EVENT_TIMESTAMP_FORMAT )
        except ValueError as e:
            logger.debug( f'Invalid timestamp: {e}' )
            return

        # TODO Add campaign name validation when that's included in CentralNotice

        self.valid = True

        self.bot = self._data[ 'userAgent' ][ 'is_bot' ]
        self.testing = self._data[ 'event' ].get( 'testingBanner', False )
        self.banner_shown = self._data[ 'event' ][ 'statusCode' ] == '6' # Sent as string
