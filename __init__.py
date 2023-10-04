import logging, json, requests, os

import azure.functions as func


def main( req: func.HttpRequest ) -> func.HttpResponse:
    
    logging.info( 'Python HTTP trigger function processed a request.' )

    try:

        body = json.dumps( req.get_json() )
    
    except ValueError :
        
        return func.HttpResponse(
            
            "Invalid body",
            status_code = 400
        
        )
    
    if body :

        # logging.info( "1" )

        result = fnBuildResponse( body )

        # logging.info( "Final verification : " + str( result ) )
        
        return func.HttpResponse( result, mimetype = "application/json" )
    
    else :
        
        return func.HttpResponse(
            
            "Invalid body",            
            status_code = 400
        
        )
    
def fnBuildResponse( json_data ) :

    # logging.info( "2" )

    values = json.loads( json_data )[ 'values' ]
    
    # Prepare the Output before the loop
    results = {}
    results[ "values" ] = []

    translatedList = []

    translatedBlock = ""
    
    for value in values :

        recordId = value[ "recordId" ]

        try :

            # logging.info( "3" )

            assert( "data" in value ), "'data' field is required."

            data = value[ "data" ]

            assert( "merged_content" in data ), "'merged_content' field is required in 'data' object."

            inputText = data[ "merged_content" ]

            if len( inputText ) >= 50000 :

                # logging.info( "4" )

                chunkList = [ inputText[ i : i + 5000 ] for i in range( 0, len( inputText ), 5000 ) ]

                for text in chunkList :

                    detectedLanguage = fnDetectLanguage( text )

                    if detectedLanguage == "en" :

                        translatedList.append( text )
                    
                    elif detectedLanguage != None and detectedLanguage != "en"  :

                        translatedText = fnTranslateText( text, detectedLanguage )

                        translatedList.append( translatedText )

                    else :

                        logging.info( "No language detected for recordId : " + str( recordId ) )

                        assert(), "No language detected for recordId : " + str( recordId )

            else :

                # logging.info( "5" )

                detectedLanguage = fnDetectLanguage( inputText )

                if detectedLanguage == "en" :

                    translatedList.append( inputText )
                
                elif detectedLanguage != None and detectedLanguage != "en"  :

                    translatedText = fnTranslateText( inputText, detectedLanguage )

                    translatedList.append( translatedText )

                else :

                    logging.info( "No language detected for recordId : " + str( recordId ) )

                    assert(), "No language detected for recordId : " + str( recordId )

            for block in translatedList :

                # logging.info( "6" )

                translatedBlock += block

            outputJson =  {
                "recordId" : recordId ,
                "data" : { "detectedLanguage" : detectedLanguage ,
                    "translatedtext" : translatedBlock }
                }
            
            results[ "values" ].append( outputJson )

            jsonResponse = json.dumps( results )

            # logging.info( "7" )

            return jsonResponse

        except AssertionError as err :

            return(
                {
                    "recordID" : recordId ,
                    "errors" : [ { "message" : "Error:" + err } ]
                }
            )

def fnDetectLanguage( value ) :

    input = []

    apiEndpoint = os.getenv( "TranslateEndpoint" )
    apiAction = "detect?api-version=3.0"

    apiKey = os.getenv( "TranslateKey" )
    
    headers = {
	    'Ocp-Apim-Subscription-Key': apiKey ,
	    'Content-Type': 'application/json'
    }

    inputJson = { "Text" : value }

    input.append( inputJson )

    requestUrl = apiEndpoint + apiAction

    request = requests.post( requestUrl, headers = headers, json = input )

    response = request.json()

    # logging.info( "Response for Language Detection : " + str( response ) )

    detectedLanguage = response[ 0 ][ "language" ]

    # logging.info( "Response for Language Detection : " + str( detectedLanguage ) )

    return detectedLanguage


def fnTranslateText( text, currLanguage = None ) :

    body = [{
        "text" : text
    }]

    apiEndpoint = os.getenv( "TranslateEndpoint" )
    apiAction = "translate?api-version=3.0"

    apiKey = os.getenv( "TranslateKey" )

    headers = {
	    'Ocp-Apim-Subscription-Key': apiKey ,
	    'Content-Type': 'application/json'
    }

    params = {
        "from" : currLanguage ,
        "to" : "en"
    }

    requestUrl = apiEndpoint + apiAction

    request = requests.post( requestUrl, headers = headers, params = params, json = body )

    jsonReponse = request.json()

    # logging.info( "Response for Translation : " + str( jsonReponse ) )

    translatedText = jsonReponse[ 0 ][ "translations" ][ 0 ][ "text" ]

    return translatedText
