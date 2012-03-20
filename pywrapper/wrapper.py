import urllib, urllib2, json, base64

class wrapper:
    # testing url
    task_url = "https://staging.mobileworks.com/api/v2/task/"
    
    # production url
#    task_url = "https://work.mobileworks.com/api/v2/task/"
    
    def __init__( self, username, password ):
        self.credentials = base64.encodestring( username + ':' + password )[:-1]
        

    def request( self, taskID = None ):
        url = self.task_url
        if taskID is not None:
            url += '%s/' % taskID
        req = urllib2.Request( url )
        req.add_header( 'Authorization', 'Basic ' + self.credentials )
        return req

    def postTask( self, instructions, resource, fields ):
        query = {
            'instructions': instructions,
            'resource': resource,
            'fields': fields
        }
        response = urllib2.urlopen( self.request(), json.dumps( query ) )
        return json.loads( response.read() )
        
    def taskResult( self, taskID ):
        return json.loads( urllib2.urlopen( self.request( taskID ) ).read() )


def main():
    print 'hello!'
    w = wrapper( 'prayag', 'root' )

if __name__ == '__main__':
    main()
