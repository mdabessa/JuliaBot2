from discord.ext import commands
import datetime
from dateutil.relativedelta import relativedelta
import re


STEPS = {
    "minute": ["m", "min", "minute", "minutes", "minuto", "minutos"],
    "hour": ["h", "hour", "hours", "hora", "horas", "hr", "hrs"],
    "day": ["d", "day", "days", "dia", "dias"],
    "week": ["w", "week", "weeks", "semana", "semanas"],
    "month": ["month", "months", "mes", "meses", "mês"],
    "year": ["y", "year", "years", "a", "ano", "anos"],
}


def split_word(word, reverse=False):
    if reverse:
        regex = r"(\d+)([a-zA-Z]*)"
    else:
        regex = r"([a-zA-Z]+)(\d+)"

    matches = re.findall(regex, word)
    result = []
    for match in matches:
        if reverse:
            num, chars = match
        else:
            chars, num = match

        if num:
            num = int(num)
        else:
            num = 1

        result.append([num, chars])
    return result


class Date(commands.Converter):
    async def convert(self, ctx: commands.Context, argument: str) -> datetime.datetime:
        formats = [
            "%d/%m/%Y-%H:%M",
            "%H:%M-%d/%m/%Y",
            "%d/%m/%Y",
        ]

        date = None
        for f in formats:
            try:
                date = datetime.datetime.strptime(argument, f)
                break
            except:
                continue

        if date is None:
            raise Exception(
                f"Não é possivel converter {argument} em um objeto datetime.datetime"
            )

        now = datetime.datetime.now()
        now = now.strftime("%d/%m/%Y-%H:%M")
        date_ = date.strftime("%d/%m/%Y-%H:%M")
        print(f"{now} | Date[{argument}] -> {date_}")
        return date


class DeltaToDate(commands.Converter):
    async def convert(
        self, ctx: commands.Context, argument: str, start: datetime = None
    ) -> datetime.datetime:
        if not argument[0].isdigit():
            raise Exception(f"Não é possivel converter {argument} em DeltaToDate.")

        date = start or datetime.datetime.now()

        times = {
            "year": False,
            "month": False,
            "week": False,
            "day": False,
            "hour": False,
            "minute": False,
        }

        results = split_word(argument, reverse=True)
        for res in results:
            num = res[0]
            step = None
            for key, value in STEPS.items():
                if res[1] in value:
                    step = key
                    break

            if not step:
                raise Exception(f"Não é possivel converter {res[1]} em tempo.")

            if step not in times:
                raise Exception(f"O tempo {step} não pode ser calculado.")

            times[step] = True
            date += relativedelta(**{step + "s": num})

        now = start.strftime("%d/%m/%Y-%H:%M")
        date_ = date.strftime("%d/%m/%Y-%H:%M")
        print(f"{now} | DeltaToDate[{argument}] -> {date_}")
        return date


class NextDate(commands.Converter):
    async def convert(
        self, ctx: commands.Context, argument: str, start: datetime = None
    ) -> datetime.datetime:
        if argument[0].isdigit():
            raise Exception(f"Não é possivel converter {argument} em NextDate.")

        date = start or datetime.datetime.now()

        times = {
            "year": (start.year, True),
            "month": (start.month, True),
            "day": (start.day, True),
            "hour": (start.hour, True),
            "minute": (start.minute, True),
        }

        results = split_word(argument)

        for res in results:
            step = None
            for key, value in STEPS.items():
                if res[1] in value:
                    step = key
                    break

            if not step:
                raise Exception(f"Não é possivel converter {res[1]} em tempo.")

            if step not in times:
                raise Exception(f"O tempo {step} não pode ser calculado.")

            times[step] = (res[0], False)

        print(times)

        for step, (num, _) in times.items():
            date += relativedelta(**{step: num})

            if date < start:
                index = list(STEPS.keys()).index(step)

                while True:
                    index += 1

                    if index == len(STEPS):
                        raise Exception("Data não pode ser menor que a data atual")

                    if not times[list(STEPS.keys())[index]][1]:  # if fixed go to next
                        continue

                    next_step = list(STEPS.keys())[index]
                    date += relativedelta(**{next_step + "s": 1})
                    break

        now = start.strftime("%d/%m/%Y-%H:%M")
        date_ = date.strftime("%d/%m/%Y-%H:%M")
        print(f"{now} | NextDate[{argument}] -> {date_}")
        return date
