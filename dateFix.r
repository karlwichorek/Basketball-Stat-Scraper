# dateFix.r

# Simon Swanson
# fixes stupid dates

monthLen <- function(year, month) {
    if (month %in% c(1,3,5,7,8,10,12)) { return(1:31) }
    else if (month %in% c(4,6,9,11))   { return(1:30) }
    else if (year %% 400 == 0)         { return(1:29) }
    else if (year %% 100 == 0)         { return(1:28) }
    else if (year %% 4 == 0)           { return(1:29) }
    else                               { return(1:28) }
}

fillDates <- function(year) {
    dayList <- list()
    months  <- c(10:12,1:6)
    for (month in months) {
        if (month == 1) { year <- year + 1 }
        for (day in monthLen(year, month)) {
            dayList[[length(dayList) + 1]] <- c(year, month, day)
        }
    }
    return(dayList)
}

dateLenFix <- function(date) {
    year    <- toString(date[1])
    month   <- toString(date[2])
    day     <- toString(date[3])
    oldDate <- strtoi(paste(year, month, day, sep = ""))
    if (nchar(month) < 2) { month <- paste("0", month, sep = "") }
    if (nchar(day)   < 2) { day   <- paste("0", day,   sep = "") }
    newDate <- strtoi(paste(year, month, day, sep = ""))
    return(c(oldDate, newDate))
}

dateFix <- function(filename) {
    data     <- read.csv(filename, header=TRUE)
    oldDates <- data$Date
    posDates <- fillDates(floor(oldDates[1] / 10^(floor(log10(oldDates[1])) - 3)))
    fixDates <- c()
    for (date in oldDates) {
        dateOpts <- dateLenFix(posDates[[1]])
        while (date != dateOpts[1]) {
            posDates[[1]] <- NULL
            dateOpts      <- dateLenFix(posDates[[1]])
        }
        fixDates <- c(fixDates, dateOpts[2])
    }
    if (length(fixDates) == length(oldDates)) {
        print("Exporting updates")
        data$Date <- fixDates
        write.csv(data, file = filename, row.names = FALSE)
    } else {
        print(paste("Something went wrong with file", filename))
        return(NULL)
    }
    return("Done")
}
