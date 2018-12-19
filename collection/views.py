from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect
from collection.models import Newsletter_subscriber, Simulation_model, Uploaded_dataset
from collection.forms import Subscriber_preferencesForm, Subscriber_registrationForm, Simulation_modelForm, UploadFileForm, Uploaded_datasetForm2, Uploaded_datasetForm3, Uploaded_datasetForm4, Uploaded_datasetForm5
from django.template.defaultfilters import slugify
from collection.functions import upload_data
from collection.functions import get_from_db
from django.http import HttpResponse
import json


# ===== THE WEBSITE ===================================================================
def landing_page(request):
    return render(request, 'landing_page.html')

def about(request):
    return render(request, 'about.html')

def subscribe(request):
    if request.method == 'POST':
        form_class = Subscriber_registrationForm
        form = form_class(request.POST)

        if form.is_valid():
            form.save()
            email = form.cleaned_data['email']
            subscriber = Newsletter_subscriber.objects.get(email=email)
            return redirect('subscriber_page', userid=subscriber.userid)
        else:
            return render(request, 'subscribe.html', {'error_occured': True,})
    else:
        return render(request, 'subscribe.html', {'error_occured': False,})


def contact(request):
    return render(request, 'contact.html')


def subscriber_page(request, userid):
    subscriber = Newsletter_subscriber.objects.get(userid=userid)
    
    is_post_request = False
    if request.method == 'POST':
        is_post_request = True
        form_class = Subscriber_preferencesForm
        form = form_class(data=request.POST, instance=subscriber)
        if form.is_valid():
            form.save()

    return render(request, 'subscriber_page.html', {'subscriber':subscriber, 'is_post_request':is_post_request, })


# ===== ADMIN PAGES ===================================================================

def newsletter_subscribers(request):
    newsletter_subscribers = Newsletter_subscriber.objects.all().order_by('email')
    return render(request, 'newsletter_subscribers.html', {'newsletter_subscribers': newsletter_subscribers,})



# ===== THE TOOL ===================================================================
@login_required
def main_menu(request):
    models = Simulation_model.objects.all().order_by('id') 
    return render(request, 'tree_of_knowledge_frontend/main_menu.html', {'models': models})



 # ===============================================================
 #   _    _       _                 _       _       _        
 #  | |  | |     | |               | |     | |     | |       
 #  | |  | |_ __ | | ___   __ _  __| |   __| | __ _| |_ __ _ 
 #  | |  | | '_ \| |/ _ \ / _` |/ _` |  / _` |/ _` | __/ _` |
 #  | |__| | |_) | | (_) | (_| | (_| | | (_| | (_| | || (_| |
 #   \____/| .__/|_|\___/ \__,_|\__,_|  \__,_|\__,_|\__\__,_|
 #         | |                                               
 #         |_|         
 # ===============================================================


@login_required
def upload_data1_new(request):
    errors = []
    if request.method == 'POST':
        form1 = UploadFileForm(request.POST, request.FILES)
        if not form1.is_valid():
            errors.append("Error: Form not valid.")
        else:
            data_file = request.FILES['file']
            if data_file.name[-4:] !=".csv":
                errors.append("Error: Uploaded file is not a csv-file.")
            else:
                (upload_id, upload_error, new_errors) = upload_data.save_new_upload_details(request)
                if upload_error:
                    errors.extend(new_errors)
                    return render(request, 'tree_of_knowledge_frontend/upload_data1.html', {'upload_error':upload_error, 'errors': errors})
                else:
                    return redirect('upload_data1', upload_id=upload_id)

        # return render(request, 'tree_of_knowledge_frontend/upload_data1.html', {'errors': errors})
        return redirect('upload_data1', upload_id=upload_id, errors=errors)
    else:
        return render(request, 'tree_of_knowledge_frontend/upload_data1.html', {'errors': errors})



@login_required
def upload_data1(request, upload_id, errors=[]):
    # if the upload_id was wrong, send the user back to the first page
    uploaded_dataset = Uploaded_dataset.objects.get(id=upload_id, user=request.user)
    if uploaded_dataset is None:
        errors.append('Error: %s is not a valid upload_id' % str(upload_id))
        return render(request, 'tree_of_knowledge_frontend/upload_data1.html', {'errors': errors})

    if request.method == 'POST':
        form1 = UploadFileForm(request.POST, request.FILES)
        if not form1.is_valid():
            errors.append("Error: Form not valid.")
        else:
            data_file = request.FILES['file']
            if data_file.name[-4:] !=".csv":
                errors.append("Error: Uploaded file is not a csv-file.")
            else:
                (upload_error, new_errors) = upload_data.save_existing_upload_details(upload_id, request)
                if upload_error:
                    errors.extend(new_errors)
                    return render(request, 'tree_of_knowledge_frontend/upload_data1.html', {'upload_error':upload_error, 'errors': errors, 'uploaded_dataset':uploaded_dataset})
                else:
                    return redirect('upload_data1', upload_id=upload_id)

    return render(request, 'tree_of_knowledge_frontend/upload_data1.html', {'uploaded_dataset': uploaded_dataset, 'errors': errors})




@login_required
def upload_data2(request, upload_id):
    errors = []
    # if the upload_id was wrong, send the user back to the first page
    uploaded_dataset = Uploaded_dataset.objects.get(id=upload_id, user=request.user)
    if uploaded_dataset is None:
        errors.append('Error: %s is not a valid upload_id' % str(upload_id))
        return render(request, 'tree_of_knowledge_frontend/upload_data1.html', {'errors': errors})

    if request.method == 'POST':
        form2 = Uploaded_datasetForm2(data=request.POST, instance=uploaded_dataset)
        if not form2.is_valid():
            errors.append('Error: the form is not valid.')
        else:
            form2.save()
            return redirect('upload_data3', upload_id=upload_id)

    known_data_sources = get_from_db.get_known_data_sources()
    return render(request, 'tree_of_knowledge_frontend/upload_data2.html', {'uploaded_dataset': uploaded_dataset, 'known_data_sources': known_data_sources, 'errors': errors})


@login_required
def upload_data3(request, upload_id):
    errors = []
    # if the upload_id was wrong, send the user back to the first page
    uploaded_dataset = Uploaded_dataset.objects.get(id=upload_id, user=request.user)
    if uploaded_dataset is None:
        errors.append('Error: %s is not a valid upload_id' % str(upload_id))
        return render(request, 'tree_of_knowledge_frontend/upload_data1.html', {'errors': errors})

    
    if request.method == 'POST':
        form3 = Uploaded_datasetForm3(data=request.POST, instance=uploaded_dataset)
        if not form3.is_valid():
            errors.append('Error: the form is not valid.')
        else:
            form3.save()
            return redirect('upload_data4', upload_id=upload_id)

    object_hierachy_tree = get_from_db.get_object_hierachy_tree()
    return render(request, 'tree_of_knowledge_frontend/upload_data3.html', {'uploaded_dataset': uploaded_dataset, 'object_hierachy_tree':object_hierachy_tree, 'errors': errors})



@login_required
def upload_data4(request, upload_id):
    errors = []
    # if the upload_id was wrong, send the user back to the first page
    uploaded_dataset = Uploaded_dataset.objects.get(id=upload_id, user=request.user)
    if uploaded_dataset is None:
        errors.append('Error: %s is not a valid upload_id' % str(upload_id))
        return render(request, 'tree_of_knowledge_frontend/upload_data1.html', {'errors': errors})

    
    if request.method == 'POST':
        form4 = Uploaded_datasetForm4(data=request.POST, instance=uploaded_dataset)
        if not form4.is_valid():
            errors.append('Error: the form is not valid.')
        else:
            form4.save()
            return redirect('upload_data5', upload_id=upload_id)
 
    return render(request, 'tree_of_knowledge_frontend/upload_data4.html', {'uploaded_dataset': uploaded_dataset, 'errors': errors})



@login_required
def upload_data5(request, upload_id):
    errors = []
    # if the upload_id was wrong, send the user back to the first page
    uploaded_dataset = Uploaded_dataset.objects.get(id=upload_id, user=request.user)
    if uploaded_dataset is None:
        errors.append('Error: %s is not a valid upload_id' % str(upload_id))
        return render(request, 'tree_of_knowledge_frontend/upload_data1.html', {'errors': errors})

    
    if request.method == 'POST':
        form5 = Uploaded_datasetForm5(data=request.POST, instance=uploaded_dataset)
        if not form5.is_valid():
            errors.append('Error: the form is not valid.')
        else:
            form5.save()
            return redirect('main_menu')
   
    return render(request, 'tree_of_knowledge_frontend/upload_data4.html', {'uploaded_dataset': uploaded_dataset, 'errors': errors})



@login_required
def get_suggested_attributes(request):
    print("upload_id = %s" % request.GET.get('upload_id', ''))
    print("attributenumber = %s" % request.GET.get('attributenumber', ''))

    returned_dict = [    {'attribute_name':'option 1', 'number_of_conflicting_values':0, 'conflicting_rows':[], 'description':'this is the best option! :)', "format": { "type": "string", "min_length": 3, "max_length": 11, "max_nulls": 0 }},
                        {'attribute_name':'option 2', 'number_of_conflicting_values':1, 'conflicting_rows':[5], 'description':'this is a great option!', "format": { "type": "date", "min": "1954-04-26 00:00:00", "max": "2009-12-17 00:00:00", "max_nulls": 0 }},
                        {'attribute_name':'option 3', 'number_of_conflicting_values':4, 'conflicting_rows':[2,5,9,24], 'description':'this is a good option! ', "format": { "type": "string", "min_length": 7, "max_length": 8, "max_nulls": 0, "allowed_values": [ "sleeping", "working" ] }},
                        {'attribute_name':'option 4', 'number_of_conflicting_values':7, 'conflicting_rows':[1,5,9,12,27, 28, 29], 'description':'this is an ok option.', "format": { "type": "string", "min_length": 4, "max_length": 52, "max_nulls": 0 }},
                        {'attribute_name':'option 5', 'number_of_conflicting_values':9, 'conflicting_rows':[3,5,6,18,23,25,29,30,31], 'description':'this is a bad option.', "format": { "type": "int", "min": 1995, "max": 2011, "sign": "positive", "max_nulls": 0 }},
                        {'attribute_name':'option 6', 'number_of_conflicting_values':15, 'conflicting_rows':[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15], 'description':'this is a option...', "format": { "type": "int", "min": 0, "max": 45559, "sign": "non-negative", "max_nulls": 0 }}]
    return HttpResponse(json.dumps(returned_dict))


@login_required
def edit_model(request, id):
    model = Simulation_model.objects.get(id=id)
    form_class = Simulation_modelForm
    form = form_class(data=request.POST, instance=model)

    if model.is_private and (model.user != request.user):
        raise Http404

    if request.method == 'POST':
        if form.is_valid():
            model = form.save(commit=False)
            model.user = request.user
            model.save()

    return render(request, 'tree_of_knowledge_frontend/edit_model.html', {'model':model, 'form': form,})



@login_required
def new_model(request):
    
    if request.method == 'POST':
        form_class = Simulation_modelForm
        form = form_class(data=request.POST)

        if form.is_valid():
            model = form.save(commit=False)
            model.user = request.user
            model.save()
            return redirect('edit_model', id= model.id)

    form_class = Simulation_modelForm
    form = form_class()
    return render(request, 'tree_of_knowledge_frontend/edit_model.html', {'form': form,})


# =======================================================================================
def test_page(request):
    # ds_names = ['3 Round Stones, Inc.', '48 Factoring Inc.', '5PSolutions', 'Abt Associates', 'Accela', 'Accenture', 'AccuWeather', 'Acxiom', 'Adaptive', 'Adobe Digital Government', 'Aidin', 'Alarm.com', 'Allianz', 'Allied Van Lines', 'Alltuition', 'Altova', 'Amazon Web Services', 'American Red Ball Movers', 'Amida Technology Solutions', 'Analytica', 'Apextech LLC', 'Appallicious', 'Aquicore', 'Archimedes Inc.', 'AreaVibes Inc.', 'Arpin Van Lines', 'Arrive Labs', 'ASC Partners', 'Asset4', 'Atlas Van Lines', 'AtSite', 'Aunt Bertha, Inc.', 'Aureus Sciences (*Now part of Elsevier)', 'AutoGrid Systems', 'Avalara', 'Avvo', 'Ayasdi', 'Azavea', 'BaleFire Global', 'Barchart', 'Be Informed', 'Bekins', 'Berkery Noyes MandASoft', 'Berkshire Hathaway', 'BetterLesson', 'BillGuard', 'Bing', 'Biovia', 'BizVizz', 'BlackRock', 'Bloomberg', 'Booz Allen Hamilton', 'Boston Consulting Group', 'Boundless', 'Bridgewater', 'Brightscope', 'BuildFax', 'Buildingeye', 'BuildZoom', 'Business and Legal Resources', 'Business Monitor International', 'Calcbench, Inc.', 'Cambridge Information Group', 'Cambridge Semantics', 'CAN Capital', 'Canon', 'Capital Cube', 'Cappex', 'Captricity', 'CareSet Systems', 'Careset.com', 'CARFAX', 'Caspio', 'Castle Biosciences', 'CB Insights', 'Ceiba Solutions', 'Center for Responsive Politics', 'Cerner', 'Certara', 'CGI', 'Charles River Associates', 'Charles Schwab Corp.', 'Chemical Abstracts Service', 'Child Care Desk', 'Chubb', 'Citigroup', 'CityScan', 'CitySourced', 'Civic Impulse LLC', 'Civic Insight', 'Civinomics', 'Civis Analytics', 'Clean Power Finance', 'ClearHealthCosts', 'ClearStory Data', 'Climate Corporation', 'CliniCast', 'Cloudmade', 'Cloudspyre', 'Code for America', 'Code-N', 'Collective IP', 'College Abacus, an ECMC initiative', 'College Board', 'Communitech', 'Compared Care', 'Compendia Bioscience Life Technologies', 'Compliance and Risks', 'Computer Packages Inc', 'CONNECT-DOT LLC.', 'ConnectEDU', 'Connotate', 'Construction Monitor LLC', 'Consumer Reports', 'CoolClimate', 'Copyright Clearance Center', 'CoreLogic', 'CostQuest', 'Credit Karma', 'Credit Sesame', 'CrowdANALYTIX', 'Dabo Health', 'DataLogix', 'DataMade', 'DataMarket', 'Datamyne', 'DataWeave', 'Deloitte', 'DemystData', 'Department of Better Technology', 'Development Seed', 'Docket Alarm, Inc.', 'Dow Jones & Co.', 'Dun & Bradstreet', 'Earth Networks', 'EarthObserver App', 'Earthquake Alert!', 'Eat Shop Sleep', 'Ecodesk', 'eInstitutional', 'Embark', 'EMC', 'Energy Points, Inc.', 'Energy Solutions Forum', 'Enervee Corporation', 'Enigma.io', 'Ensco', 'Environmental Data Resources', 'Epsilon', 'Equal Pay for Women', 'Equifax', 'Equilar', 'Ernst & Young LLP', 'eScholar LLC.', 'Esri', 'Estately', 'Everyday Health', 'Evidera', 'Experian', 'Expert Health Data Programming, Inc.', 'Exversion', 'Ez-XBRL', 'Factset', 'Factual', 'Farmers', 'FarmLogs', 'Fastcase', 'Fidelity Investments', 'FindTheBest.com', 'First Fuel Software', 'FirstPoint, Inc.', 'Fitch', 'FlightAware', 'FlightStats', 'FlightView', 'Food+Tech Connect', 'Forrester Research', 'Foursquare', 'Fujitsu', 'Funding Circle', 'FutureAdvisor', 'Fuzion Apps, Inc.', 'Gallup', 'Galorath Incorporated', 'Garmin', 'Genability', 'GenoSpace', 'Geofeedia', 'Geolytics', 'Geoscape', 'GetRaised', 'GitHub', 'Glassy Media', 'Golden Helix', 'GoodGuide', 'Google Maps', 'Google Public Data Explorer', 'Government Transaction Services', 'Govini', 'GovTribe', 'Govzilla, Inc.', 'gRadiant Research LLC', 'Graebel Van Lines', 'Graematter, Inc.', 'Granicus', 'GreatSchools', 'GuideStar', 'H3 Biomedicine', 'Harris Corporation', 'HDScores, Inc', 'Headlight', 'Healthgrades', 'Healthline', 'HealthMap', 'HealthPocket, Inc.', 'HelloWallet', 'HERE', 'Honest Buildings', 'HopStop', 'Housefax', "How's My Offer?", 'IBM', 'ideas42', 'iFactor Consulting', 'IFI CLAIMS Patent Services', 'iMedicare', 'Impact Forecasting (Aon)', 'Impaq International', 'Import.io', 'IMS Health', 'InCadence', 'indoo.rs', 'InfoCommerce Group', 'Informatica', 'InnoCentive', 'Innography', 'Innovest Systems', 'Inovalon', 'Inrix Traffic', 'Intelius', 'Intermap Technologies', 'Investormill', 'Iodine', 'IPHIX', 'iRecycle', 'iTriage', 'IVES Group Inc', 'IW Financial', 'JJ Keller', 'J.P. Morgan Chase', 'Junar, Inc.', 'Junyo', 'Kaiser Permanante', 'karmadata', 'Keychain Logistics Corp.', 'KidAdmit, Inc.', 'Kimono Labs', 'KLD Research', 'Knoema', 'Knoema Corporation', 'Knowledge Agency', 'KPMG', 'Kroll Bond Ratings Agency', 'Kyruus', 'Lawdragon', 'Legal Science Partners', '(Leg)Cyte', 'LegiNation, Inc.', 'LegiStorm', 'Lenddo', 'Lending Club', 'Level One Technologies', 'LexisNexis', 'Liberty Mutual Insurance Cos.', 'Lilly Open Innovation Drug Discovery', 'Liquid Robotics', 'Locavore', 'LOGIXDATA, LLC', 'LoopNet', 'Loqate, Inc.', 'LoseIt.com', 'LOVELAND Technologies', 'Lucid', 'Lumesis, Inc.', 'Mango Transit', 'Mapbox', 'Maponics', 'MapQuest', 'Marinexplore, Inc.', 'MarketSense', 'Marlin & Associates', 'Marlin Alter and Associates', 'McGraw Hill Financial', 'McKinsey', 'MedWatcher', 'Mercaris', 'Merrill Corp.', 'Merrill Lynch', 'MetLife', 'mHealthCoach', 'MicroBilt Corporation', 'Microsoft Windows Azure Marketplace', 'Mint', "Moody's", 'Morgan Stanley', 'Morningstar, Inc.', 'Mozio', 'MuckRock.com', 'Munetrix', 'Municode', 'National Van Lines', 'Nationwide Mutual Insurance Company', 'Nautilytics', 'Navico', 'NERA Economic Consulting', 'NerdWallet', 'New Media Parents', 'Next Step Living', 'NextBus', 'nGAP Incorporated', 'Nielsen', 'Noesis', 'NonprofitMetrics', 'North American Van Lines', 'Noveda Technologies', 'NuCivic', 'Numedii', 'Oliver Wyman', 'OnDeck', 'OnStar', 'Ontodia, Inc', 'Onvia', 'Open Data Nation', 'OpenCounter', 'OpenGov', 'OpenPlans', 'OpportunitySpace, Inc.', 'Optensity', 'optiGov', 'OptumInsight', 'Orlin Research', 'OSIsoft', 'OTC Markets', 'Outline', 'Oversight Systems', 'Overture Technologies', 'Owler', 'Palantir Technologies', 'Panjiva', 'Parsons Brinckerhoff', 'Patently-O', 'PatientsLikeMe', 'Pave', 'Paxata', 'PayScale, Inc.', 'PeerJ', 'People Power', 'Persint', 'Personal Democracy Media', 'Personal, Inc.', 'Personalis', "Peterson's", 'PEV4me.com', 'PIXIA Corp', 'PlaceILive.com', 'PlanetEcosystems', 'PlotWatt', 'Plus-U', 'PolicyMap', 'Politify', 'Poncho App', 'POPVOX', 'Porch', 'PossibilityU', 'PowerAdvocate', 'Practice Fusion', 'Predilytics', 'PricewaterhouseCoopers (PWC)', 'ProgrammableWeb', 'Progressive Insurance Group', 'Propeller Health', 'ProPublica', 'PublicEngines', 'PYA Analytics', 'Qado Energy, Inc.', 'Quandl', 'Quertle', 'Quid', 'R R Donnelley', 'RAND Corporation', 'Rand McNally', 'Rank and Filed', 'Ranku', 'Rapid Cycle Solutions', 'realtor.com', 'Recargo', 'ReciPal', 'Redfin', 'RedLaser', 'Reed Elsevier', 'REI Systems', 'Relationship Science', 'Remi', 'Rentlogic', 'Retroficiency', 'Revaluate', 'Revelstone', 'Rezolve Group', 'Rivet Software', 'Roadify Transit', 'Robinson + Yu', 'Russell Investments', 'Sage Bionetworks', 'SAP', 'SAS', 'Scale Unlimited', 'Science Exchange', 'Seabourne', 'SeeClickFix', 'SigFig', 'Simple Energy', 'SimpleTuition', 'SlashDB', 'Smart Utility Systems', 'SmartAsset', 'SmartProcure', 'Smartronix', 'SnapSense', 'Social Explorer', 'Social Health Insights', 'SocialEffort Inc', 'Socrata', 'Solar Census', 'SolarList', 'Sophic Systems Alliance', 'S&P Capital IQ', 'SpaceCurve', 'SpeSo Health', 'Spikes Cavell Analytic Inc', 'Splunk', 'Spokeo', 'SpotCrime', 'SpotHero.com', 'Stamen Design', "Standard and Poor's", 'State Farm Insurance', 'Sterling Infosystems', 'Stevens Worldwide Van Lines', 'STILLWATER SUPERCOMPUTING INC', 'StockSmart', 'Stormpulse', 'StreamLink Software', 'StreetCred Software, Inc', 'StreetEasy', 'Suddath', 'Symcat', 'Synthicity', 'T. Rowe Price', 'Tableau Software', 'TagniFi', 'Telenav', 'Tendril', 'Teradata', 'The Advisory Board Company', 'The Bridgespan Group', 'The DocGraph Journal', 'The Govtech Fund', 'The Schork Report', 'The Vanguard Group', 'Think Computer Corporation', 'Thinknum', 'Thomson Reuters', 'TopCoder', 'TowerData', 'TransparaGov', 'TransUnion', 'TrialTrove', 'TrialX', 'Trintech', 'TrueCar', 'Trulia', 'TrustedID', 'TuvaLabs', 'Uber', 'Unigo LLC', 'United Mayflower', 'Urban Airship', 'Urban Mapping, Inc', 'US Green Data', 'U.S. News Schools', 'USAA Group', 'USSearch', 'Verdafero', 'Vimo', 'VisualDoD, LLC', 'Vital Axiom | Niinja', 'VitalChek', 'Vitals', 'Vizzuality', 'Votizen', 'Walk Score', 'WaterSmart Software', 'WattzOn', 'Way Better Patents', 'Weather Channel', 'Weather Decision Technologies', 'Weather Underground', 'WebFilings', 'Webitects', 'WebMD', 'Weight Watchers', 'WeMakeItSafer', 'Wheaton World Wide Moving', 'Whitby Group', 'Wolfram Research', 'Wolters Kluwer', 'Workhands', 'Xatori', 'Xcential', 'xDayta', 'Xignite', 'Yahoo', 'Zebu Compliance Solutions', 'Yelp', 'YourMapper', 'Zillow', 'ZocDoc', 'Zonability', 'Zoner', 'Zurich Insurance (Risk Room)']
    # for ds_name in ds_names:
    #     datasource = Datasource(name=ds_name)
    #     datasource.save()
    form = Uploaded_datasetForm2()
    return render(request, 'tree_of_knowledge_frontend/test_page.html', {'form':form})