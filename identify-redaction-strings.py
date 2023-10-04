import logging, requests, json, os

import azure.functions as func


def main( req: func.HttpRequest ) -> func.HttpResponse:
    
    logging.info( "Python HTTP trigger function processed a request." )

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

    values = json.loads( json_data )[ 'values' ]

    logging.info( "Input Values : " + str( values ) )
    
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

            jsonRedactOutput = fnDetectRedactTerms( inputText)

            logging.info( "Redaction Detection Results : " + str( jsonRedactOutput ) )

            if "redactCode" in jsonRedactOutput :

                outputJson = {
                    "recordId" : recordId ,
                    "data" : jsonRedactOutput
                }

            else :

                outputJson = {
                    "recordId" : recordId ,
                    "data" : jsonRedactOutput[ "warnings" ]
                }

            results[ "values" ].append( outputJson )

            jsonReponse = json.dumps( results )

            return jsonReponse

        except AssertionError as err :

            return(
                {
                    "recordID" : recordId ,
                    "errors" : [ { "message" : "Error:" + err } ]
                }
            )
        
def fnDetectRedactTerms( text ) :

    findingsList = []

    jsonRedactList = {
            "masterSource" : "https://redactionlist.api.dod.gov" ,
            "redactList" : [ {
                "redactCode" : "Top Secret" ,
                "redactStrings" : {
                    "TS1" : "finance" ,
                    "TS2" : "alien" ,
                    "TS3" : "powerpoint",
                    "TS4" : "Top Secret"
                    }
                }, {
                "redactCode" : "For Official Use Only",
                "redactStrings" : {
                    "FOUO1" : "electronic" ,
                    "FOUO2" : "email" ,
                    "FOUO3" : "SharePoint",
                    "FOUO4" : "ACCM"
                    }
                }, {
                "redactCode" : "My God...Its Jason Bourne.",
                "redactStrings" : {
                    "JB1" : "Microsoft" ,
                    "JB2" : "Azure" ,
                    "JB3" : "PowerShell" ,
                    "JB4" : "Kennedy",
                    "JB5" : "Project Neptune Spear"
                    }
                }]
    }

    redactList = jsonRedactList[ "redactList" ]

    for item in redactList :

        typeList = item[ "redactStrings" ]
        typeCode = item[ "redactCode" ]

        for term in typeList.items() :

            termCode = term[ 0 ]
            termString = term[ 1 ]

            if termString in text :

                termIndex = text.index( termString )

                logging.info( "Identified redaction term " + termString + " at position " + str( termIndex ) + "." )

                redactJson = fnGetSentence( text, termIndex )

                findingsList.append( redactJson )

    if len( findingsList ) > 0 :
                
                jsonOutput = {
                    "redactCode" : termCode ,
                    "redactString" : termString ,
                    "redactList" : findingsList
                }

    else :

        jsonOutput = {
                    "redactCode" : "0" ,
                    "redactString" : "0" ,
                    "redactList" : [
                        { "warning" : "No redaction terms found." }
                    ]
                }

    return jsonOutput

def fnGetSentence( text, index ) :

    punctuationList = [ ".", "!", "?" ]

    startIndex = 0
    endIndex = 0

    frontHalf = text[ 0 : index ]
    backHalf = text[ index : ]

    # logging.info( "Front Half : " + frontHalf + ", Back Half : " + backHalf )

    frontList = [ *frontHalf ]
    backList = [ *backHalf ]

    # logging.info( "Front List : " + str( frontList ) )
    # logging.info( "Back List : " + str( backList ) )

    counter = -1

    while counter <= -1 :

        # logging.info( "Front Counter Value : " + str( counter ) )

        # logging.info( "frontList[ counter ] value : " + frontList[ counter ] )

        if frontList[ counter ] in punctuationList :

            startIndex = counter + 2

            counter = 1

            break

        elif frontList[ counter ] == frontList[ 0 ] :

            startIndex = 0

            counter = 1

            break

        else :

            counter = counter - 1

    frontReturn = frontHalf[ startIndex : ]

    # logging.info( "Front Return : " + frontReturn )

    counter = 0
    endLen = len( backHalf )

    while counter < endLen :

        # logging.info( "Back Counter Value : " + str( counter ) )

        # logging.info( "backList[ counter ] value : " + backList[ counter ] )

        if backList[ counter ] in punctuationList :

            endIndex = counter + 1

            counter = endLen + 1

            break

        else :

            counter = counter + 1

    endReturn = backHalf[ 0 : endIndex ]

    # logging.info( "End Return : " + endReturn )
    
    # final variable
    returnSentence = frontReturn + endReturn

    # logging.info( "Final Sentence : " + returnSentence )

    jsonReturn = {
        "foundSentence" : returnSentence ,
        "startIndex" : startIndex ,
        "endIndex" : endIndex
    }

    return jsonReturn



