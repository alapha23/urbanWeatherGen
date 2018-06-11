from UWG import UWG
import cProfile, pstats, StringIO
#import re

pr = cProfile.Profile()
pr.enable()
# Define the .epw, .uwg filenames to create an UWG object.
# UWG will look for the .epw file in the UWG/resources/epw folder,
# and the .uwg file in the UWG/resources/parameters folder.
epw_filename = "SGP_Singapore.486980_IWEC.epw"      # EPW file name
param_filename = "initialize_singapore.uwg"         # .uwg file name

# Initialize the UWG object and run the simulation
uwg = UWG(epw_filename, param_filename)
uwg.run()

pr.disable()
s = StringIO.StringIO()
sortby = 'cumulative'
ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
ps.print_stats()
print s.getvalue()
