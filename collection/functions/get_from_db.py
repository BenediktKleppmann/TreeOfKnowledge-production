from collection.models import Uploaded_dataset, Object_types, Attribute, Object, Data_point
import json
import pandas as pd

def get_object_hierachy_tree():
    hierachy_objects = Object_types.objects.all()

    object_hierachy_tree = []
    for hierachy_object in hierachy_objects:
        object_dict = {}
        object_dict['id'] = hierachy_object.id
        object_dict['parent'] = hierachy_object.parent
        object_dict['text'] = hierachy_object.name
        if hierachy_object.li_attr is not None:
            # print("UUUUUUUUUUUUUUUUUUUUUUUUUUUUUU")
            # print(hierachy_object.name)
            # print(hierachy_object.id)
            # print(hierachy_object.li_attr)
            # print(hierachy_object.a_attr)
            # print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
            object_dict['li_attr'] = json.loads(hierachy_object.li_attr)
        if hierachy_object.a_attr is not None:
            object_dict['a_attr'] = json.loads(hierachy_object.a_attr)
        
        object_hierachy_tree.append(object_dict)
    object_hierachy_tree_json = json.dumps(object_hierachy_tree)
    return object_hierachy_tree_json
    # return [{"id":"n1", "text" : "Thing", "li_attr": {}, "parent":"#"}, {"id":"n2", "text" : "Object" , "li_attr": {}, "parent":"n1"}, {"id":"n3", "text": "Living thing", "li_attr": {}, "parent":"n2"}, {"id":"n4", "text": "Plant", "li_attr": {"attribute_values": [{"attribute":"Kingdom", "operation":"=", "value":"Plantae"}, {"attribute":"Does photosynthesis", "operation": "=", "value":true}]}, "a_attr":{"scientific":["Plantae"]}, "parent":"n3"}, {"id":"n5", "text": "Tree", "li_attr": {"attribute_values": [{"attribute":"Has woody tissue", "operation": "=", "value":true},{"attribute":"Age", "operation": "<", "value":"7000"}]},  "parent":"n4"}, {"id":"n6", "text": "Oak", "li_attr": {"attribute_values": [{"attribute":"Produces nuts", "operation": "=", "value":true}, {"attribute":"Has leaves", "operation": "=", "value":true}, {"attribute":"Age", "operation": "<", "value":"700"}, {"attribute":"Age", "operation": "<", "value":"100"}, {"attribute":"Weight", "operation": "<", "value":"9000"}]}, "a_attr":{"synonyms": ["oak tree"], "scientific": ["Quercus"]}, "parent":"n5"}, {"id":"n7", "text": "Chestnut", "li_attr": {"attribute_values": [{"attribute":"Produces nuts", "operation": "=", "value":true}, {"attribute":"Produces berries", "operation": "=", "value":false}, {"attribute":"Age", "operation": "<", "value":"400"}, {"attribute":"Height", "operation": "<", "value":"130"}, {"attribute":"Weight", "operation": "<", "value":"10000"}]}, "a_attr":{"scientific": ["Castanea"]}, "parent":"n5"}, {"id":"n8", "text": "Flower", "li_attr": {"attribute_values": [{"attribute":"Has petals", "operation": "=", "value":true}]}, "parent":"n4"}, {"id":"n9", "text": "Lily", "li_attr": {"attribute_values": [{"attribute":"Petal color", "operation": "=", "value":"yellow"}]}, "parent":"n8"}, {"id":"n10", "text": "Animal", "li_attr": {"attribute_values": [{"attribute":"Kingdom", "operation": "=", "value":"Animalia"}]}, "a_attr":{"synonyms": ["Creature"], "scientific": ["Animalia"]}, "parent":"n2"} ]




def get_known_data_sources():
    return json.dumps(list(Uploaded_dataset.objects.order_by().values_list('data_source', flat=True).distinct()))
    # return ['3 Round Stones, Inc.', '48 Factoring Inc.', '5PSolutions', 'Abt Associates', 'Accela', 'Accenture', 'AccuWeather', 'Acxiom', 'Adaptive', 'Adobe Digital Government', 'Aidin', 'Alarm.com', 'Allianz', 'Allied Van Lines', 'Alltuition', 'Altova', 'Amazon Web Services', 'American Red Ball Movers', 'Amida Technology Solutions', 'Analytica', 'Apextech LLC', 'Appallicious', 'Aquicore', 'Archimedes Inc.', 'AreaVibes Inc.', 'Arpin Van Lines', 'Arrive Labs', 'ASC Partners', 'Asset4', 'Atlas Van Lines', 'AtSite', 'Aunt Bertha, Inc.', 'Aureus Sciences (*Now part of Elsevier)', 'AutoGrid Systems', 'Avalara', 'Avvo', 'Ayasdi', 'Azavea', 'BaleFire Global', 'Barchart', 'Be Informed', 'Bekins', 'Berkery Noyes MandASoft', 'Berkshire Hathaway', 'BetterLesson', 'BillGuard', 'Bing', 'Biovia', 'BizVizz', 'BlackRock', 'Bloomberg', 'Booz Allen Hamilton', 'Boston Consulting Group', 'Boundless', 'Bridgewater', 'Brightscope', 'BuildFax', 'Buildingeye', 'BuildZoom', 'Business and Legal Resources', 'Business Monitor International', 'Calcbench, Inc.', 'Cambridge Information Group', 'Cambridge Semantics', 'CAN Capital', 'Canon', 'Capital Cube', 'Cappex', 'Captricity', 'CareSet Systems', 'Careset.com', 'CARFAX', 'Caspio', 'Castle Biosciences', 'CB Insights', 'Ceiba Solutions', 'Center for Responsive Politics', 'Cerner', 'Certara', 'CGI', 'Charles River Associates', 'Charles Schwab Corp.', 'Chemical Abstracts Service', 'Child Care Desk', 'Chubb', 'Citigroup', 'CityScan', 'CitySourced', 'Civic Impulse LLC', 'Civic Insight', 'Civinomics', 'Civis Analytics', 'Clean Power Finance', 'ClearHealthCosts', 'ClearStory Data', 'Climate Corporation', 'CliniCast', 'Cloudmade', 'Cloudspyre', 'Code for America', 'Code-N', 'Collective IP', 'College Abacus, an ECMC initiative', 'College Board', 'Communitech', 'Compared Care', 'Compendia Bioscience Life Technologies', 'Compliance and Risks', 'Computer Packages Inc', 'CONNECT-DOT LLC.', 'ConnectEDU', 'Connotate', 'Construction Monitor LLC', 'Consumer Reports', 'CoolClimate', 'Copyright Clearance Center', 'CoreLogic', 'CostQuest', 'Credit Karma', 'Credit Sesame', 'CrowdANALYTIX', 'Dabo Health', 'DataLogix', 'DataMade', 'DataMarket', 'Datamyne', 'DataWeave', 'Deloitte', 'DemystData', 'Department of Better Technology', 'Development Seed', 'Docket Alarm, Inc.', 'Dow Jones & Co.', 'Dun & Bradstreet', 'Earth Networks', 'EarthObserver App', 'Earthquake Alert!', 'Eat Shop Sleep', 'Ecodesk', 'eInstitutional', 'Embark', 'EMC', 'Energy Points, Inc.', 'Energy Solutions Forum', 'Enervee Corporation', 'Enigma.io', 'Ensco', 'Environmental Data Resources', 'Epsilon', 'Equal Pay for Women', 'Equifax', 'Equilar', 'Ernst & Young LLP', 'eScholar LLC.', 'Esri', 'Estately', 'Everyday Health', 'Evidera', 'Experian', 'Expert Health Data Programming, Inc.', 'Exversion', 'Ez-XBRL', 'Factset', 'Factual', 'Farmers', 'FarmLogs', 'Fastcase', 'Fidelity Investments', 'FindTheBest.com', 'First Fuel Software', 'FirstPoint, Inc.', 'Fitch', 'FlightAware', 'FlightStats', 'FlightView', 'Food+Tech Connect', 'Forrester Research', 'Foursquare', 'Fujitsu', 'Funding Circle', 'FutureAdvisor', 'Fuzion Apps, Inc.', 'Gallup', 'Galorath Incorporated', 'Garmin', 'Genability', 'GenoSpace', 'Geofeedia', 'Geolytics', 'Geoscape', 'GetRaised', 'GitHub', 'Glassy Media', 'Golden Helix', 'GoodGuide', 'Google Maps', 'Google Public Data Explorer', 'Government Transaction Services', 'Govini', 'GovTribe', 'Govzilla, Inc.', 'gRadiant Research LLC', 'Graebel Van Lines', 'Graematter, Inc.', 'Granicus', 'GreatSchools', 'GuideStar', 'H3 Biomedicine', 'Harris Corporation', 'HDScores, Inc', 'Headlight', 'Healthgrades', 'Healthline', 'HealthMap', 'HealthPocket, Inc.', 'HelloWallet', 'HERE', 'Honest Buildings', 'HopStop', 'Housefax', "How's My Offer?", 'IBM', 'ideas42', 'iFactor Consulting', 'IFI CLAIMS Patent Services', 'iMedicare', 'Impact Forecasting (Aon)', 'Impaq International', 'Import.io', 'IMS Health', 'InCadence', 'indoo.rs', 'InfoCommerce Group', 'Informatica', 'InnoCentive', 'Innography', 'Innovest Systems', 'Inovalon', 'Inrix Traffic', 'Intelius', 'Intermap Technologies', 'Investormill', 'Iodine', 'IPHIX', 'iRecycle', 'iTriage', 'IVES Group Inc', 'IW Financial', 'JJ Keller', 'J.P. Morgan Chase', 'Junar, Inc.', 'Junyo', 'Kaiser Permanante', 'karmadata', 'Keychain Logistics Corp.', 'KidAdmit, Inc.', 'Kimono Labs', 'KLD Research', 'Knoema', 'Knoema Corporation', 'Knowledge Agency', 'KPMG', 'Kroll Bond Ratings Agency', 'Kyruus', 'Lawdragon', 'Legal Science Partners', '(Leg)Cyte', 'LegiNation, Inc.', 'LegiStorm', 'Lenddo', 'Lending Club', 'Level One Technologies', 'LexisNexis', 'Liberty Mutual Insurance Cos.', 'Lilly Open Innovation Drug Discovery', 'Liquid Robotics', 'Locavore', 'LOGIXDATA, LLC', 'LoopNet', 'Loqate, Inc.', 'LoseIt.com', 'LOVELAND Technologies', 'Lucid', 'Lumesis, Inc.', 'Mango Transit', 'Mapbox', 'Maponics', 'MapQuest', 'Marinexplore, Inc.', 'MarketSense', 'Marlin & Associates', 'Marlin Alter and Associates', 'McGraw Hill Financial', 'McKinsey', 'MedWatcher', 'Mercaris', 'Merrill Corp.', 'Merrill Lynch', 'MetLife', 'mHealthCoach', 'MicroBilt Corporation', 'Microsoft Windows Azure Marketplace', 'Mint', "Moody's", 'Morgan Stanley', 'Morningstar, Inc.', 'Mozio', 'MuckRock.com', 'Munetrix', 'Municode', 'National Van Lines', 'Nationwide Mutual Insurance Company', 'Nautilytics', 'Navico', 'NERA Economic Consulting', 'NerdWallet', 'New Media Parents', 'Next Step Living', 'NextBus', 'nGAP Incorporated', 'Nielsen', 'Noesis', 'NonprofitMetrics', 'North American Van Lines', 'Noveda Technologies', 'NuCivic', 'Numedii', 'Oliver Wyman', 'OnDeck', 'OnStar', 'Ontodia, Inc', 'Onvia', 'Open Data Nation', 'OpenCounter', 'OpenGov', 'OpenPlans', 'OpportunitySpace, Inc.', 'Optensity', 'optiGov', 'OptumInsight', 'Orlin Research', 'OSIsoft', 'OTC Markets', 'Outline', 'Oversight Systems', 'Overture Technologies', 'Owler', 'Palantir Technologies', 'Panjiva', 'Parsons Brinckerhoff', 'Patently-O', 'PatientsLikeMe', 'Pave', 'Paxata', 'PayScale, Inc.', 'PeerJ', 'People Power', 'Persint', 'Personal Democracy Media', 'Personal, Inc.', 'Personalis', "Peterson's", 'PEV4me.com', 'PIXIA Corp', 'PlaceILive.com', 'PlanetEcosystems', 'PlotWatt', 'Plus-U', 'PolicyMap', 'Politify', 'Poncho App', 'POPVOX', 'Porch', 'PossibilityU', 'PowerAdvocate', 'Practice Fusion', 'Predilytics', 'PricewaterhouseCoopers (PWC)', 'ProgrammableWeb', 'Progressive Insurance Group', 'Propeller Health', 'ProPublica', 'PublicEngines', 'PYA Analytics', 'Qado Energy, Inc.', 'Quandl', 'Quertle', 'Quid', 'R R Donnelley', 'RAND Corporation', 'Rand McNally', 'Rank and Filed', 'Ranku', 'Rapid Cycle Solutions', 'realtor.com', 'Recargo', 'ReciPal', 'Redfin', 'RedLaser', 'Reed Elsevier', 'REI Systems', 'Relationship Science', 'Remi', 'Rentlogic', 'Retroficiency', 'Revaluate', 'Revelstone', 'Rezolve Group', 'Rivet Software', 'Roadify Transit', 'Robinson + Yu', 'Russell Investments', 'Sage Bionetworks', 'SAP', 'SAS', 'Scale Unlimited', 'Science Exchange', 'Seabourne', 'SeeClickFix', 'SigFig', 'Simple Energy', 'SimpleTuition', 'SlashDB', 'Smart Utility Systems', 'SmartAsset', 'SmartProcure', 'Smartronix', 'SnapSense', 'Social Explorer', 'Social Health Insights', 'SocialEffort Inc', 'Socrata', 'Solar Census', 'SolarList', 'Sophic Systems Alliance', 'S&P Capital IQ', 'SpaceCurve', 'SpeSo Health', 'Spikes Cavell Analytic Inc', 'Splunk', 'Spokeo', 'SpotCrime', 'SpotHero.com', 'Stamen Design', "Standard and Poor's", 'State Farm Insurance', 'Sterling Infosystems', 'Stevens Worldwide Van Lines', 'STILLWATER SUPERCOMPUTING INC', 'StockSmart', 'Stormpulse', 'StreamLink Software', 'StreetCred Software, Inc', 'StreetEasy', 'Suddath', 'Symcat', 'Synthicity', 'T. Rowe Price', 'Tableau Software', 'TagniFi', 'Telenav', 'Tendril', 'Teradata', 'The Advisory Board Company', 'The Bridgespan Group', 'The DocGraph Journal', 'The Govtech Fund', 'The Schork Report', 'The Vanguard Group', 'Think Computer Corporation', 'Thinknum', 'Thomson Reuters', 'TopCoder', 'TowerData', 'TransparaGov', 'TransUnion', 'TrialTrove', 'TrialX', 'Trintech', 'TrueCar', 'Trulia', 'TrustedID', 'TuvaLabs', 'Uber', 'Unigo LLC', 'United Mayflower', 'Urban Airship', 'Urban Mapping, Inc', 'US Green Data', 'U.S. News Schools', 'USAA Group', 'USSearch', 'Verdafero', 'Vimo', 'VisualDoD, LLC', 'Vital Axiom | Niinja', 'VitalChek', 'Vitals', 'Vizzuality', 'Votizen', 'Walk Score', 'WaterSmart Software', 'WattzOn', 'Way Better Patents', 'Weather Channel', 'Weather Decision Technologies', 'Weather Underground', 'WebFilings', 'Webitects', 'WebMD', 'Weight Watchers', 'WeMakeItSafer', 'Wheaton World Wide Moving', 'Whitby Group', 'Wolfram Research', 'Wolters Kluwer', 'Workhands', 'Xatori', 'Xcential', 'xDayta', 'Xignite', 'Yahoo', 'Zebu Compliance Solutions', 'Yelp', 'YourMapper', 'Zillow', 'ZocDoc', 'Zonability', 'Zoner', 'Zurich Insurance (Risk Room)']

def get_list_of_parent_objects(object_type_id):
    list_of_parent_objects = []
    current_object_type = Object_types.objects.filter(id=object_type_id).first()

    while(current_object_type is not None):
        list_of_parent_objects.append({'id':current_object_type.id, 'name':current_object_type.name})
        current_object_type = Object_types.objects.filter(id=current_object_type.parent).first()

    return list_of_parent_objects


def get_list_of_child_objects(object_type_id):
    # add the value from this generation
    current_generation = Object_types.objects.filter(id=object_type_id)
    list_of_child_objects = list(current_generation.values('id', 'name'))
    
    # successively add the values from the children 
    previous_generations_ids = [object_type_id]
    while len(previous_generations_ids)>0:
        current_generation = Object_types.objects.filter(parent__in=previous_generations_ids)
        list_of_child_objects += list(current_generation.values('id', 'name'))
        previous_generations_ids = current_generation.values_list('id', flat=True)

    return list_of_child_objects



def get_data_points(object_type_id, filter_facts):

    child_object_types = get_list_of_child_objects(object_type_id)
    child_object_ids = [el['id'] for el in child_object_types]
    objects_with_suitable_otype = Object.objects.filter(object_type_id__in=child_object_ids).values_list('id', flat=True)
    data_point_records = Data_point.objects.filter(object_id__in=objects_with_suitable_otype)

    # apply the filters
    for filter_fact in filter_facts:
        if filter_fact['operation'] == '=':
            data_point_records = data_point_records.filter(attribute_id=filter_fact['attribute_id'],string_value=str(filter_fact['value']))           
        elif filter_fact['operation'] == '>':
            data_point_records = data_point_records.filter(attribute_id=filter_fact['attribute_id'],numeric_value__gt=filter_fact['value'])           
        elif filter_fact['operation'] == '<':
            data_point_records = data_point_records.filter(attribute_id=filter_fact['attribute_id'],numeric_value__lt=filter_fact['value'])           
        elif filter_fact['operation'] == 'in':
            values = [str(value) for value in filter_fact['value']]
            data_point_records = data_point_records.filter(attribute_id=filter_fact['attribute_id'],string_value__in=values)           

    # make long table with all datapoints of the found objects
    found_objects = list(set(data_point_records.values_list('object_id', flat=True)))
    all_data_points = Data_point.objects.filter(object_id__in=found_objects)
    if len(found_objects) > 0:
        long_table_df = pd.DataFrame(list(all_data_points.values()))
        long_table_df = long_table_df.sort_values(['data_quality','valid_time_end'])
        long_table_df = long_table_df.drop_duplicates(subset=['object_id','attribute_id'], keep='first')
        long_table_df = long_table_df[['object_id','attribute_id', 'string_value', 'numeric_value','boolean_value' ]]

        # pivot the long table
        long_table_df = long_table_df.reindex()
        long_table_df.set_index(['object_id','attribute_id'],inplace=True)
        broad_table_df = long_table_df.unstack('attribute_id')

        # there are columns for the different datatypes, determine which to keep
        columns_to_keep = []
        for column in broad_table_df.columns:
            attribute_data_type = Attribute.objects.get(id=column[1]).data_type
            if attribute_data_type=='string' and column[0]=='string_value':
                columns_to_keep.append(column)
            elif attribute_data_type in ['real', 'int'] and column[0]=='numeric_value':
                columns_to_keep.append(column)
            elif attribute_data_type == 'boolean' and column[0]=='boolean_value':
                columns_to_keep.append(column)

        broad_table_df = broad_table_df[columns_to_keep]
        new_column_names = [column[1] for column in columns_to_keep]
        broad_table_df.columns = new_column_names
        
        # for response: list of the tables' attributes sorted with best populated first
        table_attributes = []
        sorted_attribute_ids = broad_table_df.isnull().sum(0).sort_values(ascending=False).index
        sorted_attribute_ids = [int(attribute_id) for attribute_id in list(sorted_attribute_ids)]
        for attribute_id in sorted_attribute_ids:
            attribute_record = Attribute.objects.get(id=attribute_id)
            table_attributes.append({'attribute_id':attribute_id, 'attribute_name':attribute_record.name})


        # sort broad_table_df (the best-populated entities to the top)
        broad_table_df = broad_table_df.loc[broad_table_df.isnull().sum(1).sort_values().index]

        # prepare response
        broad_table_df['object_id'] = broad_table_df.index
        broad_table_df = broad_table_df.where(pd.notnull(broad_table_df), None)
        table_body = broad_table_df.to_dict('list')

        response = {}
        response['table_body'] = table_body
        response['table_attributes'] = table_attributes
        response['number_of_entities_found'] = len(found_objects)
    else:
        response = {}
        response['table_body'] = {}
        response['table_attributes'] = []
        response['number_of_entities_found'] = len(found_objects)

    return response


# ================================================================
# COMPILED ATTRIBUTE FORMAT
# ================================================================

# this is just a helper function for get_from_db.get_attributes_concluding_format
def compare_facts_with_format_specification(list_of_facts, attribute_id, source_of_the_facts, format_specification, comments):
    for fact in list_of_facts:
            if (fact['attribute_id'] == attribute_id):
                if (format_specification['type'] in ['int', 'real']) and (fact['operation'] in ['<', '>']):
                    # print("VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV")
                    # print(format_specification)
                    # # print(type(fact['value']))
                    # # print(type(['max']))
                    # print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
                    if(fact['operation'] == '<') and (fact['value'] < format_specification['max']):
                        # LOWER MAX FOUND
                        format_specification['max'] = fact['value']
                        comments['max'] +=  source_of_the_facts + ' -> ' + fact['attribute'] + ' ' + fact['operation'] + ' ' + str(fact['value']) + '.<br />'

                    if(fact['operation'] == '>') and (fact['value'] < format_specification['min']):
                        # LOWER MAX FOUND
                        format_specification['min'] = fact['value']
                        comments['min'] +=  source_of_the_facts + ' -> ' + fact['attribute'] + ' ' + fact['operation'] + ' ' + str(fact['value']) + '.<br />'

                if (format_specification['type'] == 'string') and (fact['operation'] == 'in'):
                    if ('allowed_values' in format_specification.keys()):
                        set_original = set(format_specification['allowed_values'])
                        set_fact = json.loads(fact['value'])
                        new_allowed_values = list(set.intersection(set1, set2))
                        if len(new_allowed_values) < format_specification['allowed_values']:
                            format_specification['allowed_values'] = new_allowed_values
                            comments['allowed_values'] += source_of_the_facts + ' -> ' + fact['attribute'] + ' ' + fact['operation'] + ' ' + str(fact['value']) + '.<br />'
                    else:
                        format_specification['allowed_values'] = json.loads(fact['value'])
                        comments['allowed_values'] += source_of_the_facts + ' -> ' + fact['attribute'] + ' ' + fact['operation'] + ' ' + str(fact['value']) + '.<br />'
    return (format_specification, comments)


def get_attributes_concluding_format(attribute_id, object_type_id, upload_id):
    list_of_parent_objects = get_list_of_parent_objects(object_type_id)
    list_of_parent_objects.reverse()

    attribute_record = Attribute.objects.get(id=attribute_id)
    constraint_dict =  json.loads(attribute_record.format_specification)
    format_specification  = constraint_dict['fields']['column']
    comments = {'min':'','max':'','allowed_values':''}
    
    # Additional Format Restrictions from the Object Type 
    for parent_object in list_of_parent_objects:
        parent_object_record = Object_types.objects.get(id=parent_object['id'])
        li_attr = json.loads(parent_object_record.li_attr)
        if (li_attr != {}):
            (format_specification, comments) = compare_facts_with_format_specification(li_attr['attribute_values'], attribute_id,  parent_object_record.name, format_specification, comments)
           
    # Additional Format Restrictions from the Meta Data
    uploaded_dataset = Uploaded_dataset.objects.get(id=upload_id)
    meta_data_facts_list = json.loads(uploaded_dataset.meta_data_facts)
    (format_specification, comments) = compare_facts_with_format_specification(meta_data_facts_list, attribute_id, "Meta Data", format_specification, comments)

    concluding_format = {}
    concluding_format['format_specification'] = format_specification
    concluding_format['comments'] = comments
    return concluding_format


def convert_fact_values_to_the_right_format(facts):
    updated_facts = []
    for fact in facts:
        attribute = Attribute.objects.get(id=fact['attribute_id'])
        data_type = json.loads(attribute.format_specification)['fields']['column']['type']
        if data_type == 'int':
            fact['value'] = int(fact['value'])
        elif data_type == 'real':
            fact['value'] = float(fact['value'])
        elif data_type == 'bool':
            if fact['value'].lower() in ['true','tru', 'ture','tue','t']:
                fact['value'] = True
            else:
                fact['value'] = False
        updated_facts.append(fact)

    return updated_facts
                     
        


