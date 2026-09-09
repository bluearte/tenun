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
    from_space: str = ""
    to_space: str = ""
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
    width: Dimension = Field(default_factory=Dimension)
    height: Dimension = Field(default_factory=Dimension)
    description: str = ""


class Coordinate(BaseModel):
    """
        Coordinate schema
    """
    x: Dimension = Field(default_factory=Dimension)
    y: Dimension = Field(default_factory=Dimension)


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
    value: tuple[float] = Field(default=(1.0, 1.0, 1.0, 1.0), min_length=3, max_length=4)


class FontBackground(BaseModel):
    """
        FontBackground schema
    """
    color: Color = Field(default_factory=Color)
    dilate: int = 5


class Text(BaseModel):
    """
        Text schema
    """
    category: typing.Literal["text"] = "text"
    value: str = ""
    position: Coordinate = Field(default_factory=Coordinate)
    size: Font = Field(default_factory=Font)
    name: str = ""
    color: Color = Field(default_factory=Color)
    background: FontBackground | None = None
    align: TextAlignment = TextAlignment(x="baseline", y="center")
    description: str = ""


class Box(BaseModel):
    """
        Box schema
    """
    category: typing.Literal["box"] = "box"
    start: Coordinate = Field(default_factory=Coordinate)
    end: Coordinate = Field(default_factory=Coordinate)
    color: Color = Field(validate_default=Color)
    thickness: int = 2
    fill: bool = True
    description: str = ""


class Line(BaseModel):
    """
        Line schema
    """
    category: typing.Literal["line"] = "line"
    start: Coordinate = Field(default_factory=Coordinate)
    end: Coordinate = Field(default_factory=Coordinate)
    color: Color = Field(default_factory=Color)
    description: str = ""


BurnIn = typing.Annotated[Text | Box | Line, Field(discriminator="category")]


class BurnIns(RootModel[list[BurnIn]]):
    """
        BurnIns schema

        This is intentionally a mixed list: each item may be a Text, Box, or Line,
        and the item is chosen by its `category` field.
    """
    root: list[BurnIn] = Field(default_factory=lambda: [BurnIn])

    # Compatibility workaround:
    # allow list-like access via data[0]
    # while still using a RootModel for top-level list validation
    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, index):
        return self.root[index]

    def __len__(self):
        return len(self.root)


class Image(BaseModel):
    """
        Image schema
    """
    resolution: Resolution = Field(default_factory=Resolution)
    position: Coordinate = Field(default_factory=Coordinate)
    colorspace: Colorspace = Field(default_factory=Colorspace)
    burn_ins: list[BurnIn] | None = None
    description: str = ""


class Images(RootModel[list[Image]]):
    """
        Images schema
    """
    root: list[Image] = Field(default_factory=lambda: [Image])

    # Compatibility workaround:
    # allow list-like access via data[0]
    # while still using a RootModel for top-level list validation
    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, index):
        return self.root[index]

    def __len__(self):
        return len(self.root)


class Preset(BaseModel):
    """
        Preset schema
    """
    target: Image = Field(default_factory=Image)
    sources: Images = Field(default_factory=Images)
    description: str = ""
