'''
This file contains the model definitions for growlproxy.
'''

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship, backref

Base = declarative_base()

class Server(Base):
    '''
    Class representing a remote growl server to send/receive notifications
    from
    '''

    __tablename__ = "Servers"

    id = Column( Integer, primary_key=True )
    name = Column( String )
    remoteHost = Column( String )
    receiveGrowls = Column( Boolean )
    forwardGrowls = Column( Boolean )
    userRegistered = Column( Boolean )   
    # True if the user registered this server.
    # False if it was registered/subscribed through gntp

    def __init__( 
            self,
            name,
            remoteHost,
            receiveGrowls=False,
            forwardGrowls=False,
            userRegistered=False
            ):
        '''
        Constructor.
        '''
        self.name = name
        self.remoteHost = remoteHost
        self.receiveGrowls = receiveGrowls
        self.forwardGrowls = forwardGrowls
        self.userRegistered = userRegistered

    def __str__( self ):
        return self.name


class ServerGroup(Base):
    '''
    Class representing a group of servers.
    Each server should have it's own server group, and new ones can be created
    when several servers need to be in the same group
    '''

    __tablename__ = "ServerGroups"

    def __init__( self, name=None ):
        self.name = name

    id = Column( Integer, primary_key=True )
    name = Column( String )
    
    # singleServerGroup should be True if this group
    # represents a single server (one of these should
    # eventually be created for each individual server)
    singleServerGroup = Column( Boolean, default=False )
    
    members = relationship(
            'ServerGroupMembership',
            backref='group',
            order_by="ServerGroupMembership.priority",
            passive_deletes=True
            )


class ServerGroupMembership(Base):
    '''
    Model to hold the membership of a server group
    '''

    __tablename__ = "ServerGroupMemberships"

    groupId = Column( 
            Integer,
            ForeignKey( 
                'ServerGroups.id', 
                onupdate='CASCADE', 
                ondelete='CASCADE' 
                ),
            primary_key = True
            )
    serverId = Column( 
            Integer,
            ForeignKey( 'Servers.id', onupdate='CASCADE', ondelete='CASCADE' ),
            primary_key = True
            )
    priority = Column( Integer, default=0 )
    # Ascending list.  If all 0, all equal priority

    #TODO: Possibly add an AssociationProxy somewhere to simplify things.
    #       At least for the server -> group relationship anyway.
    #       Probably less neccesary for the reverse`
    server = relationship(
            'Server',
            backref=backref( 'groupMemberships', passive_deletes=True )
            )


class ForwardRule(Base):
    '''
    Class representing a growl forward rule
    '''

    __tablename__ = "ForwardRules"

    id = Column( Integer, primary_key=True )
    name = Column( String )
    fromServerGroupId = Column( 
            Integer,
            ForeignKey( 
                'ServerGroups.id', 
                onupdate='CASCADE', 
                ondelete='SET NULL' 
                ) )
    toServerGroupId = Column(
            Integer,
            ForeignKey(
                'ServerGroups.id',
                onupdate='CASCADE',
                ondelete='SET NULL'
                )
            )
    
    # If True send to highest priority server
    # (Or random choice if all same priority)
    # Otherwise, send to all servers 
    # (and don't finish till done)
    sendToAll = Column( Boolean )
    
    # Store the growl for later if servers are offline
    storeIfOffline = True       

    # TODO: Find out how to make the below link straight to a list of servers?
    #       Also, maybe add a backref
    #fromServerGroup = relationship( "ServerGroup" )
    #toServerGroup = relationship( "ServerGroup" )
    # TODO: Bet the above doesn't work because there's 2 seperate things.
    #       Figure out how to fix it and then uncomment

    def __init__(
            self,
            name,
            fromServerGroupId,
            toServerGroupId,
            sendToAll=False,
            storeIfOffline=True
            ):
        """ Constructor """
        self.name = name
        self.fromServerGroupId = fromServerGroupId
        self.toServerGroupId = toServerGroupId
        self.sendToAll = sendToAll
        self.storeIfOffline = storeIfOffline


class RuleFilter(Base):
    '''
    Class representing a filter for forward rules
    Fields in this table should be ANDed together
    Rows in this table should be ORed together
    '''

    __tablename__ = "RuleFilters"

    id = Column( Integer, primary_key=True )
    ruleId = Column( 
            Integer, 
            ForeignKey( 
                'ForwardRules.id',
                onupdate='CASCADE',
                ondelete='CASCADE' 
                ) )
    applicationName = Column( String )
    growlTitle = Column( String )
    growContentsRegex = Column( String ) # Regular expression of growl contents

    #TODO: Define a constructor for the above, with default "" for all 
    #      filter criteria
    rule = relationship( 
            ForwardRule, 
            backref=backref( 'filters', passive_deletes=True )
            )


