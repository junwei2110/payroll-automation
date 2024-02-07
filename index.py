import pandas as pd
import numpy as np
from datetime import timedelta, datetime, date, time
import holidays

###################################### USER INPUTS ######################################################

df = pd.read_excel("TimesheetReport20230612-20230625 - LATEST.xlsx", "Sheet1")
years = [2023]

###################################### DATE PARAMETERS ######################################################
minHours = timedelta(hours=3)
minHoursSunPubHol = timedelta(hours=4)
weekdayBonus1 = time(19,0,0)
weekdayBonus2 = time(21,0,0)
satBonus1 = time(12,30,0)
satBonus2 = time(14,30,0)
################################################################################################################

################################################ UTILS ######################################################
def convertTimeDeltatoHours(td):
    return td.total_seconds()/timedelta(hours=1).total_seconds()

def convertTimetoTimeDelta(timing):
    return datetime.combine(date.min, timing) - datetime.min

def weekNumber(typeDay, start_date):
    if typeDay == 1:
        return start_date.date().isocalendar()[1]

################################################################################################################

###################################### CHECK TYPE OF DATE ######################################################
def holidayList(years):
    holiday_list = []
    for holiday in holidays.Australia(years=years).items():
        holiday_list.append(holiday)

    holidays_df = pd.DataFrame(holiday_list, columns=["date", "holiday"])
    return holidays_df

def checkTypeDay(start_date, pub_hol):
    # 1 is weekday, 2 is sat, 3 is sun, 4 is pub hol
    pub_hol_dates = pub_hol.unique()

    if start_date.date() in pub_hol_dates:
        return 4
    
    dayNo = start_date.weekday()
    if dayNo < 5:
        return 1
    elif dayNo == 5:
        return 2
    else:
        return 3

################################################################################################################

###################################### CHECK NORMAL HOURS ######################################################
def checkNormalHours(pub_hol, start_date, start_time, end_date, end_time):
    typeOfDay = checkTypeDay(start_date, pub_hol)
    if typeOfDay != 1:
        return 0
    
    end_datetime = datetime.combine(end_date.date(), end_time)
    start_datetime = datetime.combine(start_date.date(), start_time)

    if end_date == start_date and start_time < weekdayBonus1:

        if end_time <= weekdayBonus1:
            return convertTimeDeltatoHours(max(end_datetime - start_datetime, minHours))
        else:
            return convertTimeDeltatoHours(max(datetime.combine(end_date.date(), weekdayBonus1) - start_datetime, minHours))
    
    elif end_date > start_date and start_time < weekdayBonus1:
        return convertTimeDeltatoHours(max(datetime.combine(start_date.date(), weekdayBonus1) - start_datetime, minHours))

    return 0

def newCheckNormalHours(pub_hol, start_date, totalDur, ot15Hours, ot2Hours):
    typeOfDay = checkTypeDay(start_date, pub_hol)
    if typeOfDay != 1:
        return 0
    
    td = convertTimetoTimeDelta(totalDur)
    totalHours = convertTimeDeltatoHours(td)

    if totalHours <= 3 and ot15Hours == 0 and ot2Hours == 0:
        return 3

    return totalHours - ot15Hours - ot2Hours
    
################################################################################################################

###################################### CHECK 1.25X HOURS ######################################################
def check125Hours(pub_hol, start_date, start_time, end_date, end_time):
    typeOfDay = checkTypeDay(start_date, pub_hol)
    if typeOfDay != 2:
        return 0
    
    end_datetime = datetime.combine(end_date.date(), end_time)
    start_datetime = datetime.combine(start_date.date(), start_time)

    if end_date == start_date and start_time < satBonus1:

        if end_time <= satBonus1:
            return convertTimeDeltatoHours(max(end_datetime - start_datetime, minHours))
        else:
            return convertTimeDeltatoHours(max(datetime.combine(end_date.date(), satBonus1) - start_datetime, minHours))
    
    elif end_date > start_date and start_time < satBonus1:
        return convertTimeDeltatoHours(max(datetime.combine(start_date.date(), satBonus1) - start_datetime, minHours))

    return 0
################################################################################################################

###################################### CHECK 1.5X HOURS ######################################################
def check15Hours(pub_hol, start_date, start_time, end_date, end_time):
    typeOfDay = checkTypeDay(start_date, pub_hol)
    
    end_datetime = datetime.combine(end_date.date(), end_time)
    start_datetime = datetime.combine(start_date.date(), start_time)

    if typeOfDay == 1:
        if end_date == start_date and start_time < weekdayBonus2:
            if end_time > weekdayBonus1:
                return convertTimeDeltatoHours(min(datetime.combine(end_date.date(), weekdayBonus2), end_datetime) - max(start_datetime, datetime.combine(end_date.date(), weekdayBonus1)))
        
        elif end_date > start_date and start_time < weekdayBonus2:
            return convertTimeDeltatoHours(datetime.combine(start_date.date(), weekdayBonus2) - max(start_datetime, datetime.combine(start_date.date(), weekdayBonus1)))

    if typeOfDay == 2:
        if end_date == start_date and start_time < satBonus2:
            if end_time > satBonus1:
                return convertTimeDeltatoHours(min(datetime.combine(end_date.date(), satBonus2), end_datetime) - max(start_datetime, datetime.combine(end_date.date(), satBonus1)))
        
        elif end_date > start_date and start_time < satBonus2:
            return convertTimeDeltatoHours(datetime.combine(start_date.date(), satBonus2) - max(start_datetime, datetime.combine(start_date.date(), satBonus1)))

    return 0

def check15HoursWeeklyOT(last_day_of_week, total_weekly_hours):
    if last_day_of_week == 1:
        return max(0, total_weekly_hours - 38)
    
    return 0

################################################################################################################

###################################### CHECK 1.8X HOURS ######################################################
def check18Hours(pub_hol, start_date, start_time, end_date, end_time):
    typeOfDay = checkTypeDay(start_date, pub_hol)
    if typeOfDay != 3:
        return 0
    
    end_datetime = datetime.combine(end_date.date(), end_time)
    start_datetime = datetime.combine(start_date.date(), start_time)

    return convertTimeDeltatoHours(max(end_datetime - start_datetime, minHoursSunPubHol))
        


################################################################################################################

###################################### CHECK 2X HOURS ######################################################
def check2Hours(pub_hol, start_date, start_time, end_date, end_time):
    typeOfDay = checkTypeDay(start_date, pub_hol)
    
    end_datetime = datetime.combine(end_date.date(), end_time)
    start_datetime = datetime.combine(start_date.date(), start_time)

    if typeOfDay == 1:
        if end_date > start_date or end_time > weekdayBonus2:
            return convertTimeDeltatoHours(end_datetime - max(start_datetime, datetime.combine(start_date.date(), weekdayBonus2)))
        
    if typeOfDay == 2:
        if end_date > start_date or end_time > satBonus2:
            return convertTimeDeltatoHours(end_datetime - max(start_datetime, datetime.combine(start_date.date(), satBonus2)))

    return 0
################################################################################################################

###################################### CHECK 2.2X HOURS ######################################################
def check22Hours(pub_hol, start_date, start_time, end_date, end_time):
    typeOfDay = checkTypeDay(start_date, pub_hol)
    if typeOfDay != 4:
        return 0
    
    end_datetime = datetime.combine(end_date.date(), end_time)
    start_datetime = datetime.combine(start_date.date(), start_time)

    return convertTimeDeltatoHours(max(end_datetime - start_datetime, minHoursSunPubHol))
        


################################################################################################################
    
###################################### CHECK MEAL PLAN ######################################################
def checkMealPlan(start_date, start_time, end_date, end_time):
    end_datetime = datetime.combine(end_date.date(), end_time)
    start_datetime = datetime.combine(start_date.date(), start_time)

    td_hours = convertTimeDeltatoHours(max(end_datetime - start_datetime, minHoursSunPubHol))
    meal_allowance = 0
    if td_hours > 9.5:
        meal_allowance += 16.91
    
    if td_hours > 12:
        meal_allowance += 13.54
    
    return meal_allowance

################################################################################################################






holidays_df = holidayList(years)

df["TypeDay"] = df.apply(lambda x: checkTypeDay(x["Start Date"], holidays_df["date"],), axis=1)
# df["NormalHours"] = df.apply(lambda x: checkNormalHours(holidays_df["date"], x["Start Date"], x['Start Time'], x['End Date'], x['End Time']), axis=1)
df["1.25XHours"] = df.apply(lambda x: check125Hours(holidays_df["date"], x["Start Date"], x['Start Time'], x['End Date'], x['End Time']), axis=1)
df["1.5XHours"] = df.apply(lambda x: check15Hours(holidays_df["date"], x["Start Date"], x['Start Time'], x['End Date'], x['End Time']), axis=1)
df["1.8XHours"] = df.apply(lambda x: check18Hours(holidays_df["date"], x["Start Date"], x['Start Time'], x['End Date'], x['End Time']), axis=1)
df["2XHours"] = df.apply(lambda x: check2Hours(holidays_df["date"], x["Start Date"], x['Start Time'], x['End Date'], x['End Time']), axis=1)
df["2.2XHours"] = df.apply(lambda x: check22Hours(holidays_df["date"], x["Start Date"], x['Start Time'], x['End Date'], x['End Time']), axis=1)
df["NormalHours"] = df.apply(lambda x: newCheckNormalHours(holidays_df["date"], x["Start Date"], x['Duration'], x['1.5XHours'], x['2XHours']), axis=1)
df["Meal Allowance"] = df.apply(lambda x: checkMealPlan(x["Start Date"], x['Start Time'], x['End Date'], x['End Time']), axis=1)

df["WeekNumber"] = df.apply(lambda x: weekNumber(x["TypeDay"], x["Start Date"]), axis=1)
df['Last_day_of_week'] = np.where(df.duplicated(subset=['Employee Id', 'WeekNumber'], keep='last'), 0, 1)
df["TotalWeeklyNormalHours"] = df[['Employee Id', 'NormalHours', 'WeekNumber']].groupby(["Employee Id", "WeekNumber"])["NormalHours"].transform(sum)
df["1.5XWeeklyOT"] = df.apply(lambda x: check15HoursWeeklyOT(x["Last_day_of_week"], x["TotalWeeklyNormalHours"]), axis=1)


df.to_csv('result.csv')
print(df)
