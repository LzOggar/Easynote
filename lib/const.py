# forms
AUTH = { "username":150, "email":254, "password":32 }

# models
PROFILES = { "salt":12 }
NOTES = { "name":128, "items_per_page":10 }
KEYS = { "key":32 }

# Bleach
BLEACH = { 
			"AUTHORIZED_TAGS":[ "p", "span", "ul", "li", "ol", "br", "strong", 
							  	"em", "pre", "a", "h1", "h2", "h3", "h4", "h5", "h6",
							  	"table", "thead", "tbody", "tr", "td", "hr" ],
			"AUTHORIZED_ATTRIBUTES": { "p":[ "style", "data-mce-style" ],
									   "a":[ "title", "href", "data-mce-href" ],
									   "span":[ "style", "data-mce-style" ],
									   "ul":[ "style", "data-mce-style" ],
									   "ol":[ "style", "data-mce-style" ],
									   "li":[ "style", "data-mce-style" ],
									   "h1":[ "style", "data-mce-style" ],
									   "h2":[ "style", "data-mce-style" ],
									   "h3":[ "style", "data-mce-style" ],
									   "h4":[ "style", "data-mce-style" ],
									   "h5":[ "style", "data-mce-style" ],
									   "h6":[ "style", "data-mce-style" ],
									   "table":[ "style", "data-mce-style", "data-mce-selected", 
									   			 "border", "cellspacing", "cellpadding" ],
									   "td":[ "style", "data-mce-style", "scope" ] },
			"AUTHORIZED_STYLES": [ "text-align", "vertical-align", "text-decoration", "list-style-type",
								   "padding-left", "float", "color", "background-color", "border-color", "border-collapse", 
								   "border-width", "border-style", "width", "height", "font-size" ]
		}