import datetime


class Event:
    def __init__(self, name: str, date: datetime.date):
        self.name = name
        self.date = date

    def __repr__(self):
        return f'{self.date} {self.name}'

    def __str__(self):
        return f'{self.date} {self.name}'

    def __lt__(self, other):
        if self.date != other.date:
            return self.date < other.date
        return self.name < other.name


class DeadlineUser:
    def __init__(self):
        self.deadlines = list()
        self.size = 0
        self.subscriptions = set()
    
    def findEventName(self, name : str):
        for event in self.deadlines:
            if name == event.name:
                return True
        return False
    
    def addNewEvent(self, name: str, date: datetime.date):
        event = Event(name, date)
        self.deadlines.append(event)
        self.size += 1
    
    def delEvent(self, name: str):
        for i in range(len(self.deadlines)):
            if self.deadlines[i].name == name:
                self.deadlines.pop(i)
                self.size -= 1
                return
        
    def getEarliestEvents(self, num: int):
        num = min(num, self.size)
        self.deadlines.sort()
        return self.deadlines[:num]
    
    def changeEventDate(self, name: str, newDate: datetime.date):
        for i in range(len(self.deadlines)):
            if self.deadlines[i].name == name:
                self.deadlines[i].date = newDate
                return
            
    def changeEventName(self, oldName: str, newName: str):
        for i in range(len(self.deadlines)):
            if self.deadlines[i].name == oldName:
                self.deadlines[i].name = newName
                return
    
    def getDateEvents(self, date: datetime.date):
        result = list()
        for event in self.deadlines:
            if event.date == date:
                result.append(event)
        return result
    
    def clearEvents(self):
        self.deadlines.clear()

    def delEventsBeforeDate(self, date: datetime.date):
        self.deadlines.sort()
        boarder = 0
        while boarder < self.size and self.deadlines[boarder].date < date:
            boarder += 1
        self.deadlines = self.deadlines[boarder:]

    def getEventDate(self, name: str):
        for event in self.deadlines:
            if event.name == name:
                return event.date
    
    def subscribe(self, userId):
        self.subscriptions.add(userId)
    
    def unsubscribe(self, userId):
        self.subscriptions.discard(userId)
    
    def findSubscription(self, userId):
        return userId in self.subscriptions
