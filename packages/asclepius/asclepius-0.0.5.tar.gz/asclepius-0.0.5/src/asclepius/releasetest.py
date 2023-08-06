# import Asclepius dependencies
from asclepius.instelling import GGZ, ZKH, Instelling
from asclepius.medewerker import Medewerker

# import other dependencies


class ReleaseTest:
    
    def __init__(self, gebruiker: Medewerker, losse_bestanden: bool = False):

        # Initialiseren
        self.gebruiker = gebruiker

        self.losse_bestanden = losse_bestanden
        
        return None
    
    def test_bi(self, *instellingen: GGZ|Instelling|ZKH):
        from asclepius.regressietest import RegressieTest, TestExcel

        te = TestExcel(join_col = 'Titel', header_row = 0, test_cols = ['Norm', 'Realisatie'])

        # import hardcoded information from fileserver
        import sys
        sys.path.append(r'\\fileserver.valuecare.local\Algemeen\Automatisch testen\Python')
        from parameters import HardCodedParameters as HCP
        var_links = HCP.ggz_variabele_links

        rt = RegressieTest(self.gebruiker, product = 'bi', test_excel = te, variabele_links = var_links)

        rt.test(*instellingen)

        return None
    
    