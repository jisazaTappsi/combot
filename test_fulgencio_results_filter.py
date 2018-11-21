import fulgencio
import pandas as pd

COLUMNS = ['name', 'post', 'word', 'group_name', 'group_url', 'count', 'phone', 'email']

if __name__ == '__main__':
    leads_to_filter = fulgencio.get_leads_to_filter()
    results = pd.DataFrame([['prueba', 'una prueba post', 'nose que es', 'group name', 'url_name', 1, '3102342345', 'q@234.con']],
                           columns=COLUMNS,
                           index=['https://www.facebook.com/to_soy_unico'])
    results = fulgencio.filter_results_with_leads(results, leads_to_filter)
    print(results)
    fulgencio.save_leads_in_api(results)
