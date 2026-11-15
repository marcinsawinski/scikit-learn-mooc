# 📒 Workbook datasets

The workbooks (📒 pages in the menu) use their own datasets, different from
the ones of the lessons. This page is a reference: what each row is, what the
columns mean, where the data comes from and how to cite it.

It deliberately shows **no statistics and no plots**. Getting to know the data
is part of the workbooks, and some of them are built around something you are
meant to find yourself.

All the files are in the
[`datasets`](https://github.com/marcinsawinski/scikit-learn-mooc/tree/main/datasets)
folder of the repository.

| Dataset | File | Rows | Used in | What is predicted |
|---|---|---|---|---|
| [Wages](wages-dataset) | `cps_85_wages.csv` | 534 | M1.01, M1.02, M1.03 | whether a person earns more than $10 an hour |
| [Concrete](concrete-dataset) | `concrete_strength.csv` | 1030 | M2.01, M2.02, M2.03 | the strength of a concrete sample |
| [Spam](spam-dataset) | `spambase.csv` | 4601 | M3.01, M3.02 | whether an e-mail is spam |
| [Traffic](traffic-dataset) | `metro_traffic.csv` | 16 551 | M4.01, M4.02, M4.03 | the number of vehicles per hour |
| [Wine](wine-dataset) | `wine_quality.csv` | 6497 | M5.01, M5.02, M5.03 | colour, alcohol content, or quality |
| [Football](football-dataset) | `football_players.csv` | 8000 | M6.01, M6.02, M6.03 | the weekly wage of a player |
| [Parkinson's](parkinsons-dataset) | `parkinsons_telemonitoring.csv` | 5875 | M7.01, M7.02, M7.03, M7.05 | the severity of a patient's symptoms |
| [Bank calls](bank-dataset) | `bank_marketing.csv` | 12 000 | M7.04 | whether a client subscribes |

(wages-dataset)=
## Wages (1985 Current Population Survey)

Each row is one person interviewed in the United States in May 1985 for the
Current Population Survey.

| Column | Meaning |
|---|---|
| `EDUCATION` | years of education |
| `EXPERIENCE` | years of work experience |
| `AGE` | age in years |
| `WAGE` | hourly wage in dollars; the workbooks predict whether it is above 10 |
| `SEX` | `female` or `male` |
| `RACE` | `White`, `Hispanic` or `Other` |
| `SOUTH` | whether the person lives in the South of the country |
| `UNION` | whether the person is a member of a trade union |
| `MARR` | `Married` or `Unmarried` |
| `OCCUPATION` | `Management`, `Sales`, `Clerical`, `Service`, `Professional` or `Other` |
| `SECTOR` | `Manufacturing`, `Construction` or `Other` |

**Source:** [OpenML dataset 534](https://www.openml.org/d/534), from Berndt,
E. R. (1991), *The Practice of Econometrics*, Addison-Wesley. The file is used
as published.

**Licence:** public domain.

(concrete-dataset)=
## Concrete compressive strength

Each row is one concrete sample made and crushed in a laboratory. The first
seven columns are the recipe, in kilograms of ingredient per cubic metre of
concrete.

| Column | Meaning |
|---|---|
| `cement` | cement (kg/m³) |
| `slag` | blast-furnace slag, a by-product of steel making used in place of part of the cement (kg/m³) |
| `fly_ash` | fly ash, a by-product of coal power plants, also a cement substitute (kg/m³) |
| `water` | water (kg/m³) |
| `superplasticizer` | an additive that makes the mix more fluid with less water (kg/m³) |
| `coarse_aggregate` | gravel (kg/m³) |
| `fine_aggregate` | sand (kg/m³) |
| `age` | number of days the sample hardened before the test |
| `strength` | pressure the sample withstood before breaking, in megapascals (MPa); the target |

**Source:** [UCI Machine Learning Repository, Concrete Compressive
Strength](https://archive.ics.uci.edu/dataset/165/concrete+compressive+strength).
The columns were renamed; the rows are unchanged.

**Licence:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
Yeh, I. (1998). Concrete Compressive Strength [Dataset]. UCI Machine Learning
Repository. <https://doi.org/10.24432/C5PK67>

(spam-dataset)=
## Spam e-mails (Spambase)

Each row is one e-mail collected at Hewlett-Packard Labs in the late 1990s. The text
of the e-mails is not available: each one is described by 57 counts.

| Columns | Meaning |
|---|---|
| `word_freq_<word>` (48 columns) | how often the word appears, as a percentage of all the words of the e-mail |
| `char_freq_<character>` (6 columns) | how often the character appears, as a percentage of all the characters: `semicolon` (;), `parenthesis` ((), `bracket` ([), `exclamation` (!), `dollar` ($), `hash` (#) |
| `capital_run_length_average` | average length of the uninterrupted sequences of capital letters |
| `capital_run_length_longest` | length of the longest such sequence |
| `capital_run_length_total` | total number of capital letters in the e-mail |
| `is_spam` | 1 for an unwanted e-mail, 0 for a normal one; the target |

The 48 words are: make, address, all, 3d, our, over, remove, internet, order,
mail, receive, will, people, report, addresses, free, business, email, you,
credit, your, font, 000, money, hp, hpl, george, 650, lab, labs, telnet, 857,
data, 415, 85, technology, 1999, parts, pm, direct, cs, meeting, original,
project, re, edu, table, conference. Some of them (`hp`, `george`, `650`…)
are specific to the laboratory where the e-mails were collected: the name of
the company, of a colleague, a telephone prefix.

**Source:** [UCI Machine Learning Repository,
Spambase](https://archive.ics.uci.edu/dataset/94/spambase). The six character
columns and the target were renamed; the rows are unchanged.

**Licence:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
Hopkins, M., Reeber, E., Forman, G., & Suermondt, J. (1999). Spambase
[Dataset]. UCI Machine Learning Repository. <https://doi.org/10.24432/C53G6X>

(traffic-dataset)=
## Motorway traffic (Metro Interstate Traffic Volume)

Each row is one hour at a counting station on Interstate 94, between
Minneapolis and Saint Paul (Minnesota, USA), for the westbound direction, with
the weather during that hour.

| Column | Meaning |
|---|---|
| `date_time` | the hour the row describes (local time) |
| `holiday` | name of the public holiday, or `No holiday` |
| `temp` | average temperature in kelvin (subtract 273.15 for degrees Celsius) |
| `rain_1h` | rain during the hour, in millimetres |
| `snow_1h` | snow during the hour, in millimetres |
| `clouds_all` | cloud cover, in percent |
| `weather_main` | one-word description of the weather (`Clear`, `Clouds`, `Rain`, `Snow`, `Mist`…) |
| `traffic_volume` | number of vehicles counted during the hour; the target |

**Source:** [UCI Machine Learning Repository, Metro Interstate Traffic
Volume](https://archive.ics.uci.edu/dataset/492/metro+interstate+traffic+volume).

**Differences from the original:** only the years 2016 and 2017 are kept; when
the original has several rows for the same hour, the first one is kept; the
holiday name, given only at midnight in the original, is repeated for every
hour of the day; the detailed weather description was dropped. The values
themselves are untouched.

**Licence:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
Hogue, J. (2019). Metro Interstate Traffic Volume [Dataset]. UCI Machine
Learning Repository. <https://doi.org/10.24432/C5X60B>

(wine-dataset)=
## Wine quality

Each row is one Portuguese *vinho verde* wine, red or white, analysed in a
laboratory and marked by tasters.

| Column | Meaning |
|---|---|
| `fixed_acidity` | acids that do not evaporate, mostly tartaric acid (g/dm³) |
| `volatile_acidity` | acids that evaporate, mostly acetic acid, which gives a vinegar taste (g/dm³) |
| `citric_acid` | citric acid (g/dm³) |
| `residual_sugar` | sugar left after fermentation (g/dm³) |
| `chlorides` | salt, as sodium chloride (g/dm³) |
| `free_sulfur_dioxide` | sulfur dioxide not bound to other molecules; it protects the wine (mg/dm³) |
| `total_sulfur_dioxide` | free and bound sulfur dioxide (mg/dm³) |
| `density` | density of the wine (g/cm³) |
| `pH` | acidity on the pH scale (lower is more acid) |
| `sulphates` | potassium sulphate, an additive (g/dm³) |
| `alcohol` | alcohol content (% by volume) |
| `quality` | median mark given by at least three tasters, from 0 (very bad) to 10 (excellent) |
| `color` | `red` or `white` |

The target depends on the workbook: `color` in M5.01, `alcohol` (white wines
only) in M5.02, and whether `quality` is 7 or more in M5.03.

**Source:** [UCI Machine Learning Repository, Wine
Quality](https://archive.ics.uci.edu/dataset/186/wine+quality). The red and
white files are combined, with the `color` column to tell them apart; the rows
are unchanged.

**Licence:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
Cortez, P., Cerdeira, A., Almeida, F., Matos, T., & Reis, J. (2009). Wine
Quality [Dataset]. UCI Machine Learning Repository.
<https://doi.org/10.24432/C56S3T>

(football-dataset)=
## Football players (FIFA 22)

Each row is one professional football player **as described in the video game
FIFA 22**. The ratings and the wages are the estimates of the game's editors,
not measurements or payroll data. The file contains no player names.

| Columns | Meaning |
|---|---|
| `age`, `height_cm`, `weight_kg` | age in years, height in centimetres, weight in kilograms |
| `nationality_name` | country the player represents |
| `overall` | overall rating of the player, out of 100, computed by the game from his skills and position |
| `potential` | rating the game expects the player to reach at his best, out of 100 |
| `attacking_…` (5 columns) | crossing, finishing, heading accuracy, short passing, volleys (each out of 100) |
| `skill_…` (5 columns) | dribbling, curve, free-kick accuracy, long passing, ball control |
| `movement_…` (5 columns) | acceleration, sprint speed, agility, reactions, balance |
| `defending_…` (2 columns) | standing tackle, sliding tackle |
| `goalkeeping_…` (5 columns) | diving, handling, kicking, positioning, reflexes |
| `wage_eur` | weekly wage in euros, according to the game; the target |

**Source:** [OpenML dataset 45012](https://www.openml.org/d/45012), taken from
the [FIFA 22 complete player
dataset](https://www.kaggle.com/datasets/stefanoleone992/fifa-22-complete-player-dataset)
collected by Stefano Leone.

**Differences from the original:** a random sample of 8000 of the 19 178
players of the OpenML version.

**Licence:** CC0 (public domain), as declared on OpenML and Kaggle.

(parkinsons-dataset)=
## Parkinson's telemonitoring

Each row is one voice recording made at home by a person in the early stage
of Parkinson's disease, during a six-month trial of a telemonitoring device.
There are several recordings per day of test and many days per patient.

| Columns | Meaning |
|---|---|
| `subject` | number identifying the patient |
| `age`, `sex` | age in years; sex (0 = man, 1 = woman) |
| `test_time` | days since the patient joined the trial |
| `jitter_…` (5 columns) | measures of the variation of the pitch of the voice from one vibration to the next |
| `shimmer_…` (6 columns) | measures of the variation of its loudness |
| `nhr`, `hnr` | ratios of noise to tonal components in the voice |
| `rpde`, `dfa`, `ppe` | three other measures of the irregularity of the voice signal |
| `motor_updrs` | motor part of the UPDRS, the clinical scale of the severity of the symptoms |
| `total_updrs` | total UPDRS score (higher is worse); the target |

The UPDRS scores were assessed by clinicians at the start, the middle and the
end of the trial, and filled in linearly for the days in between.

**Source:** [UCI Machine Learning Repository, Parkinsons
Telemonitoring](https://archive.ics.uci.edu/dataset/189/parkinsons+telemonitoring).
The columns were renamed; the rows are unchanged.

**Licence:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
Tsanas, A. & Little, M. (2009). Parkinsons Telemonitoring [Dataset]. UCI
Machine Learning Repository. <https://doi.org/10.24432/C5ZS3N>

(bank-dataset)=
## Bank marketing calls

Each row is one phone call made by a Portuguese bank, between 2008 and 2010,
to offer a client a term deposit (a savings product).

| Column | Meaning |
|---|---|
| `age`, `job`, `marital`, `education` | age, type of job, marital status and level of education of the client |
| `default` | whether the client has a credit in default |
| `balance` | average yearly balance of the account, in euros |
| `housing`, `loan` | whether the client has a housing loan, a personal loan |
| `contact` | how the client was reached (`cellular`, `telephone` or `unknown`) |
| `day`, `month` | day of the month and month of the call |
| `duration` | length of the call, in seconds |
| `campaign` | number of calls made to this client during this campaign, this one included |
| `pdays` | days since the client was last called in a previous campaign (−1 if never) |
| `previous` | number of calls made to this client before this campaign |
| `poutcome` | result of the previous campaign for this client |
| `subscribed` | `yes` if the client accepted the offer; the target |

**Source:** [UCI Machine Learning Repository, Bank
Marketing](https://archive.ics.uci.edu/dataset/222/bank+marketing).

**Differences from the original:** a random sample of 12 000 of the 45 211
calls, kept in their original order; the target `y` was renamed `subscribed`
and `day_of_week` renamed `day`; missing categories are written `unknown`.

**Licence:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
Moro, S., Rita, P., & Cortez, P. (2014). Bank Marketing [Dataset]. UCI Machine
Learning Repository. <https://doi.org/10.24432/C5K306>
