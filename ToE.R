library(tidyverse)
library(lubridate)
library(rnaturalearth)
library(rnaturalearthhires)
library(RColorBrewer)
library(ggthemes)
library(patchwork)

calc_indicators <- function (InDir, catchment, prob) {
  # Function for to extract yearly series of flow quantiles (e.g. Q5/Q95).
  # The threshold is calculated from a baseline period - here defined as 1981-2010. These years are inclusive.

  #  Parameters:
  #  catchment : ID of catchment to calculate indicators for
  #  prob : quantile (e.g. 0.95 for Q5, 0.05 for Q95)

  #  Returns
  #  Qsim_quantile : data frame of yearly series of flow quantiles.

  Qsim <- read.csv(paste0(InDir, "G2G_DailyRiverFlow_NATURAL_", catchment, "_19801201_20801130.csv"), skip = 45)
  Qsim <- Qsim[1:36000,]
  names(Qsim) <- c("Date", paste0("RCM",1:12))
  Qsim$year <- as.numeric(substr(Qsim$Date, 1,4))
  Qsim <- Qsim[,c(2:14)]
  
  Qsim_quantile <- Qsim %>%
    group_by(year) %>%
    summarise(across(where(is.numeric),
                     ~ quantile(.x, probs = c(prob)),
                     .names = "{.col}")) 
  Qsim_quantile <- data.frame(Qsim_quantile[Qsim_quantile$year %in% 1981:2080,])
  return (Qsim_quantile)
}

calc_seasonal_flows <- function(InDir, catchment, season) {
  # Function for to extract yearly series of seasonal flows
  # The threshold is calculated from a baseline period - here defined as 1981-2010. These years are inclusive.
  
  #  Parameters:
  #  catchment : ID of catchment to calculate indicators for
  #  season : aconym of seasons to select (i.e. DJF, MAM, JJA or SON)
  
  #  Returns
  #  Qsim_season : data frame of yearly series of average river flows for each season
  
  Qsim <- read.csv(paste0(InDir, "G2G_DailyRiverFlow_NATURAL_", catchment, "_19801201_20801130.csv"), skip = 45)
  Qsim <- Qsim[1:36000,]
  names(Qsim) <- c("Date", paste0("RCM",1:12))
  Qsim$Date <- as.Date(Qsim$Date)
  Qsim$year <- as.numeric(substr(Qsim$Date, 1,4))
  Qsim$seas <- seas::mkseas(x = Qsim, width = "DJF")
  
  Qsim_season <- Qsim[Qsim$seas %in% season,]
  Qsim_season <- aggregate(.~year, Qsim_season, FUN=mean)
  Qsim_season <- Qsim_season[,c("year", paste0("RCM",1:12))]
  return(Qsim_season)
}


KS_test <- function(Qsim, ref_start=1991, ref_end=2020) {
  # Function for to calculate the time period when statistically significant differences in  river flows
  # are detected in successive 30-year periods compared to the baseline (1991-2020). These years are inclusive.
  # Statistical significance is detected using the Kolmogrov-Smirnov test for each ensemble member independently
  # The Time of Emergence is determined as the time period when at least 4 or 8 RCMs reaches statistical significance
  #
  # Methodology from Muelchi et al., HESS 
  #  
  #  Parameters:
  #  Qsim : yearly series of either simulated river flow quantiles or seasonal average river flows
  #  ref_start : start year of reference period
  #  ref_end : end year of reference period 
  # 
  #  Returns
  #  Output : data frame of the estimated timing (end year of 30-year period) when at least 4 (1/3rds) or 8 (2/3rds) RCMs 
  #          reach statistical significance and their direction of change (-1 or 1 for negative or positive)
  
  refperiod <- Qsim[Qsim$year %in% ref_start:ref_end,]
  
  startyear <- c(1982:c(2080-29))
  KS_output <- as.data.frame(matrix(nrow=length(startyear), ncol=12))
  sign_output <- as.data.frame(matrix(nrow=length(startyear), ncol=12))
  for (year in 1:length(startyear)) {
    segment <- Qsim[Qsim$year %in% startyear[year]: c(startyear[year]+29),]
    for (em in 1:12) {
      KS_output[year,em] <- ks.test(refperiod[,paste0("RCM", em)], segment[,paste0("RCM", em)])$p.value
      sign_output[year,em] <- mean(segment[,paste0("RCM", em)]) - mean(refperiod[,paste0("RCM", em)])
    }
  }
  names(KS_output) <- paste0("RCM", 1:12)
  KS_output$endyear <- startyear + 29
  
  # detect change direction
  rows_ok <- which(rowSums(KS_output[1:12] < 0.05) >= 4)[1]
  cols_below <- lapply(rows_ok, function(r) {colnames(KS_output)[1:12][KS_output[r, 1:12] <= 0.05]})
  sign1 <- sign(mean(as.numeric(sign_output[rows_ok,which(names(KS_output) %in% cols_below[[1]])])))
  
  rows_ok <- which(rowSums(KS_output[1:12] < 0.05) >= 8)[1]
  cols_below <- lapply(rows_ok, function(r) {colnames(KS_output)[1:12][KS_output[r, 1:12] <= 0.05]})
  sign2 <- sign(mean(as.numeric(sign_output[rows_ok,which(names(KS_output) %in% cols_below[[1]])])))
  
  # detect first year when 1/3 or 2/3 of RCMs (i.e. 4 or 8 out of 12) show statistical significance. 
  ToE1 <- KS_output$endyear[which(rowSums(KS_output[,1:12] <= 0.05, na.rm = TRUE) >= 4)[1]]
  ToE2 <- KS_output$endyear[which(rowSums(KS_output[,1:12] <= 0.05, na.rm = TRUE) >= 8)[1]]
  
  return (list(ToE1, ToE2, sign1, sign2))
}

calc_ToE <- function (InDir, catchment, prob) {
  Qsim_quantiles <- calc_indicators(InDir, catchment, prob)
  ToE <- KS_test(Qsim_quantiles, ref_start = 1991, ref_end = 2020)
  output <- data.frame("ToE1" = ToE[[1]], "ToE2" = ToE[[2]], "sign1"= ToE[[3]], "sign2" = ToE[[4]], "ID" = catchment)
  return (output)
}

calc_ToE_seasonal <- function(InDir, catchment, season) {
  Qsim_season <- calc_seasonal_flows(InDir, catchment, season)
  ToE <- KS_test(Qsim_season, ref_start = 1981, ref_end = 2010)
  output <- data.frame("ToE1" = ToE[[1]], "ToE2" = ToE[[2]], "sign1"= ToE[[3]], "sign2" = ToE[[4]], "ID" = catchment)
  return (output)
}


############# RUN CODE ################
setwd("/path/to/data/")
files <- list.files()
Catchment_List <- as.numeric(substr(files, 28, 32))

# define input and output directory
InDir <- "/path/to/data/"
OutDir <- "/path/to/outputs/"

# sapply function loops over all catchment IDs within the CS-NOW G2G dataset
ToE_Q95 <- unnest(data.frame(t(sapply(Catchment_List, calc_ToE, prob=0.05, InDir=InDir))))
ToE_Q5 <- unnest(data.frame(t(sapply(Catchment_List, calc_ToE, prob=0.95, InDir=InDir))))
write.csv(ToE_Q95, paste0(OutDir, "ToE_Q95.csv"),row.names=F)
write.csv(ToE_Q5, paste0(OutDir, "ToE_Q5.csv"),row.names=F)

ToE_DJF <- unnest(data.frame(t(sapply(Catchment_List, calc_ToE_seasonal, season="DJF", InDir=InDir))))
ToE_MAM <- unnest(data.frame(t(sapply(Catchment_List, calc_ToE_seasonal, season="MAM", InDir=InDir))))
ToE_JJA <- unnest(data.frame(t(sapply(Catchment_List, calc_ToE_seasonal, season="JJA", InDir=InDir))))
ToE_SON <- unnest(data.frame(t(sapply(Catchment_List, calc_ToE_seasonal, season="SON", InDir=InDir))))
write.csv(ToE_DJF, paste0(OutDir, "ToE_DJF.csv"),row.names=F)
write.csv(ToE_MAM, paste0(OutDir, "ToE_MAM.csv"),row.names=F)
write.csv(ToE_JJA, paste0(OutDir, "ToE_JJA.csv"),row.names=F)
write.csv(ToE_SON, paste0(OutDir, "ToE_SON.csv"),row.names=F)


############# PLOTTING ################

allstations <- rnrfa::catalogue()
names(allstations)[1] <- "ID"


plot_map <- function(ToE) {
  england <- ne_countries(geounit = c("england"), type = "map_units", scale="large")
  cols <- colorRampPalette(brewer.pal(9, "YlOrRd"))(11)
  
  ToE <- ToE %>% pivot_longer(
    cols = c(ToE1, ToE2, sign1, sign2),
    names_to = c(".value", "set"),
    names_pattern = "([A-Za-z]+)(\\d)"
  ) %>%
    select(ToE, sign, ID)
  ToE$index <- rep(c(4,8), c(dim(ToE)[1]/2))
  
  ToE <- left_join(ToE, allstations, by="ID")
  ToE <- ToE[ToE$index %in% 8,]
  ToE$index <- factor(ToE$index, levels=c("4", "8"), labels=c("≥4 RCM reach significance", "≥8 RCM reach significance"))
  ToE$sign <- factor(ToE$sign, levels=c("-1", "1", "NaN"))

  plot1 <- ggplot() +
    geom_sf(data = england, fill="white", col="black") +
    geom_point(data = ToE, aes(x=longitude, y=latitude, fill=ToE, shape=sign, size=sign)) +
    scale_shape_manual(values=c(25,24, 21), drop=F) +
    scale_fill_stepsn(colours = rev(cols), breaks=seq(2030,2080,5), 
                      limits=c(2030,2080), na.value = "grey90") +
    scale_size_manual(values=c(2,2, 1)) +
    theme_map() +
    facet_wrap(~index, nrow=1) +
    labs(fill="") +
    theme_map() +
    theme(legend.position="right",plot.title=element_text(size=12, face="bold",hjust = 0.5),
          legend.justification = "center", strip.background = element_blank(), 
          strip.text = element_text(size=12, face="bold"),legend.key.height = unit(1.5, "cm"))+
    guides(shape = "none", size="none")
  
  return(plot1)
}

Q95_plot <- plot_map(ToE_Q95)
Q5_plot <- plot_map(ToE_Q5)

ggsave(paste0(OutDir, "ToE_quantiles_CSNOW.pdf"), 
       Q95_plot|Q5_plot, width=10, height=5)

# DJF_plot <- plot_map(ToE_DJF)
# MAM_plot <- plot_map(ToE_MAM)
# JJA_plot <- plot_map(ToE_JJA)
# SON_plot <- plot_map(ToE_SON)
# ggsave(paste0(OutDir, "ToE_seasonal_CSNOW.png"),
#        (DJF_plot|MAM_plot)/(JJA_plot|SON_plot), width=20, height=12)




