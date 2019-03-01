var items = [
    {type: 'item', text: 'Cut', icon: 'fa fa-scissors'},
    {type: 'item', text: 'Copy', icon: 'fa fa-files-o'},
    {type: 'item', text: 'Paste', icon: 'fa fa-clipboard'},
    {type: 'divider'},
    {type: 'item', text: 'Delete', icon: 'fa fa-times'},
];

jQuery(document).ready(function($){
    $('#context-click').contextMenu({
        transition: { type: 'fadeIn', speed: 300 },
        items: [
            {type: 'title', text: 'Page Actions'},
            {type: 'item', text: 'Back', icon: 'fa fa-arrow-left'},
            {type: 'item', text: 'Forward', icon: 'fa fa-arrow-right'},
            {type: 'item', text: 'Reload', icon: 'fa fa-refresh'},
            {type: 'divider'},
            {type: 'title', text: 'File Actions'},
            {type: 'item', text: 'Open', icon: 'fa fa-folder-open-o'},
            {type: 'item', text: 'Open with...', icon: 'fa fa-external-link', 
                items: [
                    {type: 'item', text: 'Photoshop'},
                    {type: 'item', text: 'Other...',
                        items: [
                            {type: 'item', text: 'Safari'},
                            {type: 'item', text: 'Chrome'},
                            {type: 'item', text: 'FireFox'}
                        ]
                    },
                    {type: 'item', text: 'Illustrator'},
                    {type: 'item', text: 'Paint'}
                ]
            },
            {type: 'item', text: 'Save', icon: 'fa fa-floppy-o'},
            {type: 'divider'},
            {type: 'title', text: 'Checkboxes'},
            {type: 'checkbox', text: 'Checkbox 1'},
            {type: 'checkbox', text: 'Checkbox 2', checked: true},
            {type: 'title', text: 'Disabled Actions'},
            {type: 'item', text: 'Disabled 1', disabled: true},
            {type: 'item', text: 'Disabled 2', disabled: true}
        ]
    });
    
    /*---------------------------------------------*\
     * Item Types
    \*---------------------------------------------*/
    
    $('#item-types').contextMenu({
        items: [
            {type: 'title', text: 'Title'},
            {type: 'item', text: 'Item'},
            {type: 'item', text: 'Submenu',
                items: [
                    {type: 'item', text: 'Sub-Item 1'},
                    {type: 'item', text: 'Sub-Item 2'},
                    {type: 'item', text: 'Sub-Item 3'}
                ]
            },
            {type: 'divider'},
            {type: 'checkbox', text: 'Checkbox', checked: true}
        ]
    });
    
    /*---------------------------------------------*\
     * Triggering Events
    \*---------------------------------------------*/
    
    $('.triggering-events').each(function(){
        var event = $(this).attr('data-event');
        $(this).contextMenu({
            autoHide: event === 'hover' ? 300 : false, // Wait 300ms before hiding the menu
            position: {my: 'left top+5',at: 'left bottom'},
            event: event,
            items: items
        });
    });
    
    /*---------------------------------------------*\
     * Item Events
    \*---------------------------------------------*/
    
    $('#item-events').contextMenu({
        items: [
            {type: 'item', text: 'Click Me', click: function(e) {alert('Item clicked');}},
            {type: 'item', text: 'Hover Over Me', hover: function(e) {alert('Item hovered over');}}
        ]
    });
    
    // Menu-wide
    $('#menu-wide-events').contextMenu({
        click: function(e) {alert('The item "'+this.text+'" was clicked');},
        items: [
            {type: 'item', text: 'Item 1'},
            {type: 'item', text: 'Item 2'},
            {type: 'item', text: 'Item 3', click: function(e){alert('Click event overridden by '+this.text);}}
        ]
    });
    
    /*---------------------------------------------*\
     * Transitions
    \*---------------------------------------------*/
    
    $('.transition').each(function(){
        var type  = $(this).attr('data-transition'),
            speed = type === 'none' ? 0 : 300;
        $(this).contextMenu({
            transition: {speed: speed, type: type},
            position: {my: 'left top+5',at: 'left bottom'}, // +5 to account for arrow position
            items: items
        });
    });  
    
    /*---------------------------------------------*\
     * Auto Hiding
    \*---------------------------------------------*/
    
    $('#autohide').contextMenu({
        autoHide: 500,
        transition: {speed: 300, type: 'fadeIn'},
        items: items
    });
    
    /*---------------------------------------------*\
     * Positioning
    \*---------------------------------------------*/
    
    
    $('.contextmenu-position').each(function(){
        $(this).contextMenu({
            position: {my: $(this).attr('data-position-my'),at: $(this).attr('data-position-at'), children: '.context-click-subitem'},
            items: items
        });
    });
    
    /*---------------------------------------------*\
     * Dynamic Event Binding
    \*---------------------------------------------*/
    
    $('#element-creator').click(function(e){
        e.preventDefault();
        var el = $('<div>').addClass('context-click-area dynamic').text('Right Click Here');
        $(this).parent().parent().append(el);
    });
    
    $('html').contextMenu({
        selector: '.context-click-area.dynamic',
        items: items
    });
     
    /*---------------------------------------------*\
     * Build Callback
    \*---------------------------------------------*/
    
    var activeItem;
    $('#build-callback').contextMenu({
        items: function(e) {
            return [
                {type: 'title', text: $(e.target).closest('.context-click-subitem').length ? e.target.innerHTML : 'All Items'},
                {type: 'divider'},
                {type: 'item', text: 'Cut', icon: 'fa fa-scissors'},
                {type: 'item', text: 'Copy', icon: 'fa fa-files-o'},
                {type: 'item', text: 'Paste', icon: 'fa fa-clipboard'},
            ]
        }
    });
    
    /*---------------------------------------------*\
     * Action Hooks
    \*---------------------------------------------*/
    
    var activeItem;
    $('#action-hooks').contextMenu({
        items: items,
        hooks: {
            show: function(e) {},
            position: function(e){
                if(typeof activeItem !== 'undefined')
                {
                    $(activeItem).css({'box-shadow':'none'});
                }
                activeItem = e.target;
                $(e.target).css({'box-shadow':'0 0 0 4px #f1c40f'});
            },
            hide: function(e){
                $(activeItem).css({'box-shadow':'none'});
            }
        }
    });
    
    /*---------------------------------------------*\
     * Autocomplete
    \*---------------------------------------------*/
    
    var states = {
        "AL": "Alabama",
        "AK": "Alaska",
        "AS": "American Samoa",
        "AZ": "Arizona",
        "AR": "Arkansas",
        "CA": "California",
        "CO": "Colorado",
        "CT": "Connecticut",
        "DE": "Delaware",
        "DC": "District Of Columbia",
        "FM": "Federated States Of Micronesia",
        "FL": "Florida",
        "GA": "Georgia",
        "GU": "Guam",
        "HI": "Hawaii",
        "ID": "Idaho",
        "IL": "Illinois",
        "IN": "Indiana",
        "IA": "Iowa",
        "KS": "Kansas",
        "KY": "Kentucky",
        "LA": "Louisiana",
        "ME": "Maine",
        "MH": "Marshall Islands",
        "MD": "Maryland",
        "MA": "Massachusetts",
        "MI": "Michigan",
        "MN": "Minnesota",
        "MS": "Mississippi",
        "MO": "Missouri",
        "MT": "Montana",
        "NE": "Nebraska",
        "NV": "Nevada",
        "NH": "New Hampshire",
        "NJ": "New Jersey",
        "NM": "New Mexico",
        "NY": "New York",
        "NC": "North Carolina",
        "ND": "North Dakota",
        "MP": "Northern Mariana Islands",
        "OH": "Ohio",
        "OK": "Oklahoma",
        "OR": "Oregon",
        "PW": "Palau",
        "PA": "Pennsylvania",
        "PR": "Puerto Rico",
        "RI": "Rhode Island",
        "SC": "South Carolina",
        "SD": "South Dakota",
        "TN": "Tennessee",
        "TX": "Texas",
        "UT": "Utah",
        "VT": "Vermont",
        "VI": "Virgin Islands",
        "VA": "Virginia",
        "WA": "Washington",
        "WV": "West Virginia",
        "WI": "Wisconsin",
        "WY": "Wyoming"
    };
    
    $('#autocomplete').contextMenu({
        event: 'focus',
        width: $('#autocomplete').outerWidth(),
        maxHeight: 150,
        position: {my: 'left top+5',at:'left bottom'},
        items: function(e) {
            var items = [],
                value = $('#autocomplete').val(),
                regex = new RegExp(value,'i');
        
            $.each(states,function(k,v){
                if( v.match(regex) && value.length )
                {
                    items.push({
                        type: 'item',
                        text: v.replace(regex,function(match){
                            return '<strong>' + match + '</strong>';
                        }),
                        click: function(e) {
                            $('#autocomplete').val(v);
                        }
                    });
                }
                if( items.length > 7 ) return false; // Break loop
            });
            return items;
        }
    });
    
    // Refresh list when input changes
    $('#autocomplete').on('keyup',function(e){
        var c = e.which;
        if(c !== 37 && c !== 38 && c !== 39 && c !== 40)
        {
            $(this).contextMenu('refresh',e);
            $(this).contextMenu('select',0);
        }
    });
    
    /*---------------------------------------------*\
     * Navigation
    \*---------------------------------------------*/
    
    $('#demo-nav').contextMenu({
        event: 'hover',
        position: {my: 'left top',at:'left bottom', children: 'li'},
        arrow: false,
        class: 'demo-nav-menu',
        autoHide: 300,
        maxWidth: 200,
        transition: {type: 'fadeIn',speed: 200},
        hooks: {
            // This will not be called for items with no submenu (since there are no items to show)
            // Therefore the fix at the bottom is required
            position: function(e){
                $('#demo-nav li').removeClass('hover');
                $(e.target).addClass('hover');
            },
            hide: function(e){
                $('#demo-nav li').removeClass('hover');
            }
        },
        items: function(e) {
            var items = [];
            $(e.target).closest('li').find('li').each(function(){
                var $a = $(this).children('a');
                items.push({
                    type: 'item',
                    text: $a.html(),
                    click: function(e) {window.location.href = $a.attr('href');}
                });
            });
            return items;
        }
    })
    // Fix .hover sticking to elements with submenus
    .on('mousemove','li',function(e){
        if(!$(e.target).closest('li').has('ul').length)
        {
            $('#demo-nav li').removeClass('hover');
        }
    });
});