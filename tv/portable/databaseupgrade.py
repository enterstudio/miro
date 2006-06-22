"""Responsible for upgrading old versions of the database.

NOTE: For really old versions (before the schema.py module, see
olddatabaseupgrade.py)
"""

import schema
chatter = True # set to False in the unittests

class DatabaseTooNewError(Exception):
    """Error that we raise when we see a database that is newer than the
    version that we can update too.
    """
    pass

def upgrade(savedObjects, saveVersion, upgradeTo=None):
    """Upgrade a list of SavableObjects that were saved using an old version 
    of the database schema.

    This method will call upgradeX for each number X between saveVersion and
    upgradeTo.  For example, if saveVersion is 2 and upgradeTo is 4, this
    method is equivelant to:

        upgrade3(savedObjects)
        upgrade4(savedObjects)

    By default, upgradeTo will be the VERSION variable in schema.
    """

    if upgradeTo is None:
        upgradeTo = schema.VERSION

    if saveVersion > upgradeTo:
        msg = ("Database was created by a newer version of Democracy " 
               "(db version is %s)" % saveVersion)
        raise DatabaseTooNewError(msg)

    while saveVersion < upgradeTo:
        if chatter:
            print "upgrading database to version %s" % (saveVersion + 1)
        upgradeFunc = globals()['upgrade%d' % (saveVersion + 1)]
        if upgradeFunc is not None:
            upgradeFunc(savedObjects)
        else:
            upgradeFunc = globals()['upgradeObject%d' % (saveVersion + 1)]
            for o in savedObjects:
                upgradeFunc(o)
        saveVersion += 1

def upgradeObject(object, saveVersion, upgradeTo=None):
    """Upgrade a list of SavableObjects that were saved using an old version 
    of the database schema.

    This method will call upgradeObjectX for each number X between saveVersion and
    upgradeTo.  For example, if saveVersion is 2 and upgradeTo is 4, this
    method is equivelant to:

        upgradeObject3(object)
        upgradeObject4(object)

    returning True if any of them returned True.

    upgradeObjectX should return True if it has changed the object.

    By default, upgradeTo will be the VERSION variable in schema.
    """

    retval = False

    if upgradeTo is None:
        upgradeTo = schema.VERSION

    while saveVersion < upgradeTo:
        upgradeFunc = globals()['upgradeObject%d' % (saveVersion + 1)]
        if (upgradeFunc(object)):
            retval = True
        saveVersion += 1
    return retval

def upgrade2(objectList):
    """Add a dlerType variable to all RemoteDownloader objects."""

    for o in objectList:
        if o.classString == 'remote-downloader':
            # many of our old attributes are now stored in status
            o.savedData['status'] = {}
            for key in ('startTime', 'endTime', 'filename', 'state',
                    'currentSize', 'totalSize', 'reasonFailed'):
                o.savedData['status'][key] = o.savedData[key]
                del o.savedData[key]
            # force the download daemon to create a new downloader object.
            o.savedData['dlid'] = 'noid'

def upgrade3(objectList):
    """Add the expireTime variable to FeedImpl objects."""

    for o in objectList:
        if o.classString == 'feed':
            feedImpl = o.savedData['actualFeed']
            if feedImpl is not None:
                feedImpl.savedData['expireTime'] = None

def upgrade4(objectList):
    """Add iconCache variables to all Item objects."""
    for o in objectList:
        if o.classString in ['item', 'file-item', 'feed']:
            o.savedData['iconCache'] = None

def upgrade5(objectList):
    """Upgrade metainfo from old BitTorrent format to BitTornado format"""
    for o in objectList:
        if o.classString == 'remote-downloader':
            if o.savedData['status'].has_key('metainfo'):
                o.savedData['status']['metainfo'] = None
                o.savedData['status']['infohash'] = None

def upgrade6(objectList):
    """Add downloadedTime to items."""
    for o in objectList:
        if o.classString in ('item', 'file-item'):
            o.savedData['downloadedTime'] = None

def upgrade7(objectList):
    """Add the initialUpdate variable to FeedImpl objects."""
    for o in objectList:
        if o.classString == 'feed':
            feedImpl = o.savedData['actualFeed']
            if feedImpl is not None:
                feedImpl.savedData['initialUpdate'] = False

def upgrade8(objectList):
    """Have items point to feed_id instead of feed."""
    for o in objectList:
        if o.classString in ('item', 'file-item'):
            o.savedData['feed_id'] = o.savedData['feed'].savedData['id']
            
def upgrade9(objectList):
    """Added the deleted field to file items"""
    for o in objectList:
        if o.classString == 'file-item':
            o.savedData['deleted'] = False
            
#def upgradeObjectX (o):
#    """ upgrade an object to X.  return True if object is changed and False otherwise. """
#    if objectneedschange:
#        changeObject()
#        return True
#    return False
