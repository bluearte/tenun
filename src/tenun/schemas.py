import typing

from pydantic import BaseModel, RootModel, Field


class TextAlignment(BaseModel):
    """
        Text Alignment schema
    """
    x: str = ""
    y: str = ""


class Colorspace(BaseModel):
    """
        Colorspace schema
    """
    fromspace: str = ""
    tospace: str = ""
    description: str = ""


class Dimension(BaseModel):
    """
        Dimension schema
    """
    value: int = Field(0, ge=0)
    scale: float = Field(1, gt=0)
    description: str = ""


class Resolution(BaseModel):
    """
        Resolution schema
    """
    width: Dimension = Dimension()
    height: Dimension = Dimension()
    description: str = ""


class Coordinate(BaseModel):
    """
        Coordinate schema
    """
    x: Dimension = Dimension()
    y: Dimension = Dimension()


class Font(BaseModel):
    """
        Font schema
    """
    value: int = Field(0, ge=0)
    scale: float = Field(1, gt=0)
    minimum: int = Field(8, gt=0)
    description: str = ""


class Color(BaseModel):
    """
        Color schema
    """
    value: typing.List[float] = Field([1.0, 1.0, 1.0, 1.0], min_length=3, max_length=4)


class FontBackground(BaseModel):
    """
        FontBackground schema
    """
    color: Color = Color()
    dilate: int = 5


class Text(BaseModel):
    """
        Text schema
    """
    category: typing.Literal["text"] = "text"
    value: str = ""
    position: Coordinate = Coordinate()
    size: Font = Font()
    name: str = ""
    color: Color = Color()
    bg: FontBackground | None = None
    align: TextAlignment = TextAlignment(x="baseline", y="center")
    description: str = ""


class Box(BaseModel):
    """
        Box schema
    """
    category: typing.Literal["box"] = "box"
    start: Coordinate = Coordinate()
    end: Coordinate = Coordinate()
    color: Color = Color()
    thickness: int = 2
    fill: bool = True
    description: str = ""


class Line(BaseModel):
    """
        Line schema
    """
    category: typing.Literal["box"] = "box"
    start: Coordinate = Coordinate()
    end: Coordinate = Coordinate()
    color: Color = Color()
    description: str = ""


class BurnIns(RootModel[typing.List[Text| Box| Line]]):
    """
        BurnIns schema
    """
    root: typing.List[Text| Box| Line]


class Image(BaseModel):
    """
        Image schema
    """
    resolution: Resolution = Resolution()
    position: Coordinate = Coordinate()
    colorspace: Colorspace = Colorspace()
    burn_ins: typing.List[Text| Box| Line] | None = None
    description: str = ""


class Images(RootModel[typing.List[Image]]):
    """
    """
    root: typing.List[Image] = [Image()]


class Preset(BaseModel):
    """
        Preset schema
    """
    target: Image = Image()
    sources: Images = Images()
    description: str = ""
