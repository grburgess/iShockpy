import astropy.constants as astro_constants

__all__ = ["c"]


c = astro_constants.c.to("cm/s").value
