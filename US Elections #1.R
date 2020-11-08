# install packages using install.packages('package')
library(readxl)
library(tidyverse)
library(usmap)
library(ggplot2)

# POP01.xls - Source: US Census database
# POP060210D - population density from 2010 census
county_pop <- read_excel('./data/POP01.xls', sheet = 'POP01C') %>%
	subset(select=c(Area_name, POP060210D)) %>%
	separate(col=Area_name, into=c('County','State'), sep=', ')) %>%
	drop_na()

colnames(county_pop) <- c('county', 'abbr', 'pop_density')

antijoin(county_pop, usmap::countypop)
antijoin(usmap::countypop, county_pop)
write.csv(usmap::countypop, './data/tmp/usmap_county_pop.csv')
write.csv(county, './data/tmp/usmap_county_pop.csv')
# clean the data
countypop_cleaned <- read.csv('./data/tmp/usmap_county_pop.csv')

county_pop <- county_pop %>%
	transform(county = str_c(county, ' County')) %>%
	merge(usmap::countypop_cleaned %>% subset(select = -pop_2015)) %>%
 	subset(select = -c(abbr, county))

img <- plot_usmap(data = county_pop, values = 'pop_density') + 
  labs(title = 'Population density') +
  scale_fill_continuous(low = 'white', high = 'red') + 
  theme(legend.position = 'right')

plot(img)

breaks <- c(1, 3, 10, 30, 100, 300, 1000, 3000, 10000, 30000, 100000)
img <- plot_usmap(data = county_pop, values = 'pop_density', colour=NA) + 
  labs(title = 'Population density') +
  scale_fill_continuous(high='red', low='yellow', trans='log10',
                          breaks = breaks, limits=c(0.1,70000)) + 
  theme(legend.position = 'right')

plot(img)

# countypres_2000-2016.csv - Source: MIT Election Lab
voting <- read.csv('./data/countypres_2000-2016.csv') %>%
  subset(select = c(year, FIPS, party, candidatevotes, totalvotes, county, state_po)) %>%
  drop_na()

voting$percentagevotes = voting$candidatevotes/voting$totalvotes
voting <- subset(voting, select=-c(candidatevotes, totalvotes))

library(anchors) # for replace.value()

colnames(voting)[2] <- 'fips'
voting <- voting %>% replace.value('fips', 46113, 46102)  # Shannon County -> Oglala Lakota

winner <- voting$percentagevotes %>%
  aggregate(by = list(voting$year, voting$fips), max) %>%
  setNames(c('year', 'fips', 'percentagevotes')) %>%
  merge(voting) %>%
  subset(select = -percentagevotes) %>%
  merge(county_pop)

winner$party <- as.factor(winner$party)

img <- plot_usmap(data = filter(winner, winner$year==2016), values = 'party', size=0.01) +
  labs(title = '2016 US Presidential Election') +
  scale_fill_manual(values = c('democrat'='blue', 'republican'='red'), name='party') +
  theme(legend.position = 'right')

plot(img)

library(gganimate)

anim <- plot_usmap(data = winner, values = "party") +
  labs(title = "{closest_state} US Presidential Election") +
  scale_fill_manual(values = c("democrat"="blue", "republican"="red"), name="party") +
  theme(legend.position = "right") +
  transition_states(year) +
  ease_aes('sine-in')

animate(anim, fps=20, duration=15, width=706, height=576)

library(arules) # for the discretize method

breaks <- c(0,10,100,1000,10000,100000)
types <- c('The Wilderness', 'Village', 'Town', 'City', 'Megacity')
winner$type <- winner$pop_density %>%
  discretize(method = 'fixed', breaks = breaks, labels = types)

for (year_ in unique(winner$year) %>% sort()) {
  winner_by_year <- filter(winner, winner$year == year_)
  chisq_result <- table(winner_by_year$party, winner_by_year$type) %>%
    chisq.test()
  print(year)
  print(chisq_result)
}