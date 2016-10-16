# LIPAD_analyser

##Summary:
  The Linked Parliamentary Data Project (LIPAD) is a Canadian PostgreSQL 
database indexing the past 150 years of federal parliamentary debate of the 
house of commons. The python psycopg2 code offers a new way to investigate 
this database and extract the number of time a word or expression was said 
for each parties. The following example visualisation offers a comprehensive 
investigation of environment and energy related words across time. Scrolling 
between the different words is permitted through the legend and mouseover offers
supplementary information on the graphic. The graphic shows key years in the 
evolution of our environment and energy policies. This investigation tool has
shown some correlation with world changing event. Some of these events are:
First nuclear talk after the explosion of the first nuclear bomb, increase 
discussion about petrol, oil, gas during the 1973 oil crisis and the presence of
a peak for climate change, solar power and wind power after the 1997 signature
of the kyoto protocol. These events are pointed out on the exemple visualisation.

##Content:
###HTML file:
  Exemple of a visualisation using environment and energy related key words.
Colors of words must be set in the program for different analysis.
  
###Python script:
  Extraction script using psycopg2. The list of words must be specified inside the code.
  
###csv file:
  Exemple of the non transformed csv extraction file.
  
###csv transformed file:
  Exemple of a long format csv file usable in the html visualisation program.
