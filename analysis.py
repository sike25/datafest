from variables import market_counts_by_industry, absorption_rates, expected_rent, occupancy_rates, best_times, university_enrollment, region_growth_map

nb_regions = 4
nb_markets = 29

regions = ['Midwest/Central', 'Northeast', 'South', 'West']
markets = ['Atlanta', 'Austin', 'Baltimore', 'Boston', 'Charlotte', 'Chicago', 'Chicago Suburbs', 'Dallas/Ft Worth', 'Denver', 'Detroit', 'Houston', 'Los Angeles', 'Manhattan', 'Nashville', 'Northern New Jersey', 'Northern Virginia', 'Orange County', 'Philadelphia', 'Phoenix', 'Raleigh/Durham', 'Salt Lake City', 'San Diego', 'San Francisco', 'Seattle', 'South Bay/San Jose', 'South Florida', 'Maryland', 'Tampa', 'Washington D.C.']

markets_per_region = {
    'Midwest/Central': ['Chicago', 'Chicago Suburbs', 'Denver', 'Detroit'], 
    'Northeast': ['Baltimore', 'Boston', 'Manhattan', 'Northern New Jersey', 'Northern Virginia', 'Philadelphia', 'Southern Maryland', 'Washington D.C.'], 
    'South': ['Atlanta', 'Austin', 'Charlotte', 'Dallas/Ft Worth', 'Houston', 'Nashville', 'Raleigh/Durham', 'South Florida', 'Tampa'], 
    'West': ['Los Angeles', 'Orange County', 'Phoenix', 'Salt Lake City', 'San Diego', 'San Francisco', 'Seattle', 'South Bay/San Jose']
}

industries = ['Technology, Advertising, Media, and Information', 'Financial Services and Insurance', 'Legal Services']


def collect_features(region, industry, quarter, low_budget, high_budget):

    abs_rates = []
    ind_cnts  = []
    occ_rates = []
    exp_rent  = []
    rent_dff  = []
    best_tm   = []
    econ_gt   = []
    talent_p  = []

    # collect features for each market in the region
    for market in markets_per_region[region]:
        
        # absorption rates
        absorption_0, absorption_1 = absorption_rates[market]
        absorption = absorption_0 + absorption_1
        abs_rates.append(absorption)

        # industry counts
        ind_count = market_counts_by_industry[industry][market]
        ind_cnts.append(ind_count)

        # occupancy rates
        if market in occupancy_rates:
          occupancy_rate = occupancy_rates[market]
          occ_rates.append(occupancy_rate)
        else:
          occ_rates.append(0)

        # expected prices
        rent_0, rent_1 = expected_rent[market]
        rent = (rent_0[quarter] + rent_1[quarter]) / 2
        exp_rent.append(rent)

        # distance between price and budget
        if rent < low_budget:
            rent_dff.append(low_budget - rent)
        elif rent > high_budget:
            rent_dff.append(rent - high_budget)
        else:
            rent_dff.append(0)

        # best time to find space
        best_time = best_times[market]
        best_tm.append(best_time)

        # projected economic growth
        growth = region_growth_map[market]
        econ_gt.append(growth)

        # talent pool
        talent_pool = university_enrollment[market]
        talent_pool = int(talent_pool.replace(',', '').strip())
        talent_p.append(talent_pool)
        

    return abs_rates, ind_cnts, exp_rent, occ_rates, rent_dff, best_tm, econ_gt, talent_p


def normalize_data(data):
    min_value = min(data)
    max_value = max(data)
    if max_value == min_value:
        return [0.5 for _ in data] 
    normalized_data = [(x - min_value) / (max_value - min_value) for x in data]
    return normalized_data


def make_market_recommendations(region, industry, quarter, low_budget, high_budget, talent): 
    abs_rates, ind_cnts, exp_rent, occ_rates, _, best_tm, econ_gt, talent_p = collect_features(region, industry, quarter, low_budget, high_budget)
    
    occ_rates = normalize_data(occ_rates)
    abs_rates = normalize_data(occ_rates)

    # expected price, possible space trade-offs, ease of finding space, best time to find space, ease of finding talent

    recommendations = {}
    for idx, market in enumerate(markets_per_region[region]):
        market_recommendation = {}

        market_recommendation['market'] = market
        market_recommendation['expected_price'] = exp_rent[idx]

        if occ_rates[idx] >= 0.5:
          market_recommendation['space_trade_offs'] = "less"
        else:
          market_recommendation['space_trade_offs'] = "more"

        if abs_rates[idx] >= 0.5:
          market_recommendation['ease_of_finding_space'] = "easy"
        else:
          market_recommendation['ease_of_finding_space'] = "hard"

        market_recommendation['best_time_to_find_space'] = best_tm[idx]

        market_recommendation['company_numbers'] = ind_cnts[idx]

        if talent:
          if talent_p[idx] >= 1_000_000:
            market_recommendation['ease_of_finding_talent'] = "talent standout"
          else:
            market_recommendation['ease_of_finding_talent'] = "-"

        if econ_gt[idx] >= 25_000:
          market_recommendation['economic_growth'] = "high"
        else:
          market_recommendation['economic_growth'] = "-"

        recommendations[market] = market_recommendation


    return recommendations
        

def find_best_market(region, industry, quarter, low_budget, high_budget):
    # absorption rates, no of relevant companies in area, _, average occupancy rates, difference between budget and rent in dollar/sqft/year, _, per income capita growth in 5 years, _
    abs_rates, ind_cnts, _, occ_rates, rent_dff, _, econ_gt, _ = collect_features(region, industry, quarter, low_budget, high_budget)

    abs_rates = normalize_data(abs_rates)
    ind_cnts = normalize_data(ind_cnts)
    occ_rates = normalize_data(occ_rates)
    rent_dff = normalize_data(rent_dff)
    econ_gt = normalize_data(econ_gt)

    best_market = ''
    max_score = 0

    wins_per_market = {}
    for market in markets_per_region[region]:
        wins_per_market[market] = []

    for i in range(len(markets_per_region[region])):
        
        market = markets_per_region[region][i]

        # categorize wins per market
        if abs_rates[i] > 0.8:
            wins_per_market[market].append('Strongest Absorption Rates')
        if ind_cnts[i] > 0.8:
            wins_per_market[market].append('The Most Industry-relevant Companies')
        if occ_rates[i] > 0.8:
            wins_per_market[market].append('Highest Occupancy Rates')
        if rent_dff[i] > 0.8:
            wins_per_market[market].append('Closest to Budget')
        if econ_gt[i] > 0.8:
            wins_per_market[market].append('Highest Growth Rates')
        
        score = (1.0 * abs_rates[i]) + (1.0 * ind_cnts[i]) + (0.5 * occ_rates[i]) + (0.1 * econ_gt[i]) + (1.75 * (1-rent_dff[i]))
        # score = (1.5 * abs_rates[i]) + (2.0 * ind_cnts[i]) + (1.0 * occ_rates[i]) + (0.3 * econ_gt[i]) - (2.0 * rent_dff[i])

        if score > max_score:
            max_score = score
            best_market = markets_per_region[region][i]

    best_market_wins = wins_per_market[best_market]
    return best_market, best_market_wins


# trandform the results to a list of maps (per market)
def transform_results(market_recommendations, best_market, best_market_wins, region, talent):

    transformed_results = []

    for market in markets_per_region[region]:

        recommendation = market_recommendations[market]

        n_map = {}

        # market
        n_map['market'] = market

        # best?
        if market == best_market:
            n_map['best_market'] = True
            n_map['wins'] = best_market_wins
        else:
            n_map['best_market'] = False
            n_map['wins'] = []

        # expected price
        n_map['expected_price'] = int(recommendation['expected_price'])

        # talent hub
        if talent:
          if recommendation['ease_of_finding_talent'] == 'talent standout':
              n_map['talent_hub'] = True
          else:
              n_map['talent_hub'] = False

        # econmic growth hub
        if recommendation['economic_growth'] == 'high':
            n_map['economic_growth'] = True  
        else:
            n_map['economic_growth'] = False

        n_map['details'] = []

        # space trade off
        if recommendation['space_trade_offs'] == 'more':
            n_map['details'].append('Can make small compromises on space')
        else:
            n_map['details'].append('Should not compromise on space')

        # ease of finding space
        if recommendation['ease_of_finding_space'] == 'easy':
            n_map['details'].append('Spaces can linger on the market longer')
        else:
            n_map['details'].append('Spaces get rented out quickly')

        # best time to find space
        n_map['time'] = recommendation['best_time_to_find_space']

        transformed_results.append(n_map)

    return transformed_results


# Program entry point
def start_analysis(region, industry, quarter, low_budget, high_budget, talent):

  # translate region names to match the data
  if region == 'midwest':
    region = regions[0]
  elif region == 'northeast':
    region = regions[1]
  elif region == 'south':
    region = regions[2]
  elif region == 'west':
    region = regions[3]
  else:
    raise ValueError("Invalid region name " + region) 

  # translate quarter to index
  if quarter == 'q1': quarter = 0
  elif quarter == 'q2': quarter = 1
  elif quarter == 'q3': quarter = 2
  elif quarter == 'q4': quarter = 3
  else: raise ValueError("Invalid quarter name")

  # translate industry names to indices
  if industry == 'tami':
    industry = industries[0]
  elif industry == 'fsi':
    industry = industries[1]
  elif industry == 'legal':
    industry = industries[2]
  else:
    raise ValueError("Invalid industry name")
  
  # translate budget to integers
  try:
    low_budget = int(low_budget)
    high_budget = int(high_budget)
  except ValueError:
    raise ValueError("Invalid budget value")


  # run analyses
  market_recommendations = make_market_recommendations(region, industry, quarter, low_budget, high_budget, talent)
  best_market = find_best_market(region, industry, quarter, low_budget, high_budget)
  best_market, best_market_wins = best_market[0], best_market[1]

  # clean up the recommendations
  results = transform_results(market_recommendations, best_market, best_market_wins, region, talent)

  return results

# res = start_analysis('midwest', 'legal', 'q3', 5, 90, True)
# for r in res:
#   print(r)
#   print('---')

print("Madame Saville loves datafest!")



