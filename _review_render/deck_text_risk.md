# Static Text Overflow Risk

- Source: `C:\Users\27677\Documents\ChatGPT\论文\重构版论文_v4_20260915\汇报用_论文介绍.pptx`
- Highest risk: `medium`
- Risk count: 86
- Note: Static OOXML text-density heuristic. True text bounds require PowerPoint COM rendering.

## Slide 1

| Shape | Risk | Chars | Font pt | Box pt | Estimate |
| --- | --- | ---: | ---: | --- | --- |
| TextBox 1 | `medium` | 14 | 40.0 | 828.0 x 72.0 | 39 chars / 1 lines |
| TextBox 2 | `medium` | 25 | 18.0 | 828.0 x 43.2 | 87 chars / 1 lines |
| TextBox 4 | `medium` | 13 | 12.0 | 223.2 x 21.6 | 33 chars / 1 lines |
| TextBox 5 | `medium` | 9 | 30.0 | 223.2 x 50.4 | 13 chars / 1 lines |
| TextBox 6 | `medium` | 11 | 12.0 | 223.2 x 36.0 | 33 chars / 1 lines |
| TextBox 8 | `medium` | 18 | 12.0 | 223.2 x 21.6 | 33 chars / 1 lines |
| TextBox 9 | `medium` | 9 | 30.0 | 223.2 x 50.4 | 13 chars / 1 lines |
| TextBox 10 | `medium` | 7 | 12.0 | 223.2 x 36.0 | 33 chars / 1 lines |
| TextBox 12 | `medium` | 15 | 12.0 | 223.2 x 21.6 | 33 chars / 1 lines |
| TextBox 13 | `medium` | 9 | 30.0 | 223.2 x 50.4 | 13 chars / 1 lines |
| TextBox 14 | `medium` | 19 | 12.0 | 223.2 x 36.0 | 33 chars / 1 lines |
| TextBox 15 | `medium` | 34 | 15.0 | 828.0 x 28.8 | 104 chars / 1 lines |
| TextBox 16 | `medium` | 35 | 10.0 | 648.0 x 21.6 | 122 chars / 1 lines |
| TextBox 17 | `medium` | 1 | 10.0 | 43.2 x 21.6 | 6 chars / 1 lines |

## Slide 2

| Shape | Risk | Chars | Font pt | Box pt | Estimate |
| --- | --- | ---: | ---: | --- | --- |
| TextBox 1 | `medium` | 2 | 12.0 | 864.0 x 21.6 | 136 chars / 1 lines |
| TextBox 2 | `medium` | 20 | 26.0 | 871.2 x 57.6 | 63 chars / 1 lines |
| TextBox 5 | `medium` | 8 | 16.0 | 381.6 x 28.8 | 44 chars / 1 lines |
| TextBox 8 | `medium` | 4 | 16.0 | 381.6 x 28.8 | 44 chars / 1 lines |
| TextBox 11 | `medium` | 6 | 16.0 | 381.6 x 28.8 | 44 chars / 1 lines |
| TextBox 14 | `medium` | 9 | 16.0 | 381.6 x 28.8 | 44 chars / 1 lines |
| TextBox 16 | `medium` | 47 | 13.0 | 864.0 x 28.8 | 126 chars / 1 lines |
| TextBox 17 | `medium` | 35 | 10.0 | 648.0 x 21.6 | 122 chars / 1 lines |
| TextBox 18 | `medium` | 1 | 10.0 | 43.2 x 21.6 | 6 chars / 1 lines |

## Slide 3

| Shape | Risk | Chars | Font pt | Box pt | Estimate |
| --- | --- | ---: | ---: | --- | --- |
| TextBox 1 | `medium` | 2 | 12.0 | 864.0 x 21.6 | 136 chars / 1 lines |
| TextBox 2 | `medium` | 19 | 26.0 | 871.2 x 57.6 | 63 chars / 1 lines |
| TextBox 5 | `medium` | 4 | 12.0 | 133.2 x 36.0 | 19 chars / 1 lines |
| TextBox 6 | `medium` | 1 | 16.0 | 14.4 x 28.8 | 1 chars / 1 lines |
| TextBox 8 | `medium` | 6 | 12.0 | 133.2 x 36.0 | 19 chars / 1 lines |
| TextBox 9 | `medium` | 1 | 16.0 | 14.4 x 28.8 | 1 chars / 1 lines |
| TextBox 11 | `medium` | 6 | 12.0 | 133.2 x 36.0 | 19 chars / 1 lines |
| TextBox 12 | `medium` | 1 | 16.0 | 14.4 x 28.8 | 1 chars / 1 lines |
| TextBox 14 | `medium` | 4 | 12.0 | 133.2 x 36.0 | 19 chars / 1 lines |
| TextBox 15 | `medium` | 1 | 16.0 | 14.4 x 28.8 | 1 chars / 1 lines |
| TextBox 17 | `medium` | 4 | 12.0 | 133.2 x 36.0 | 19 chars / 1 lines |
| TextBox 18 | `medium` | 1 | 16.0 | 14.4 x 28.8 | 1 chars / 1 lines |
| TextBox 20 | `medium` | 7 | 12.0 | 133.2 x 36.0 | 19 chars / 1 lines |
| TextBox 21 | `medium` | 3 | 13.0 | 108.0 x 28.8 | 14 chars / 1 lines |
| TextBox 22 | `medium` | 36 | 13.0 | 748.8 x 36.0 | 108 chars / 1 lines |
| TextBox 23 | `medium` | 4 | 13.0 | 108.0 x 28.8 | 14 chars / 1 lines |
| TextBox 24 | `medium` | 44 | 13.0 | 748.8 x 36.0 | 108 chars / 1 lines |
| TextBox 25 | `medium` | 2 | 13.0 | 108.0 x 28.8 | 14 chars / 1 lines |
| TextBox 26 | `medium` | 55 | 13.0 | 748.8 x 36.0 | 108 chars / 1 lines |
| TextBox 27 | `medium` | 2 | 13.0 | 108.0 x 28.8 | 14 chars / 1 lines |
| TextBox 28 | `medium` | 57 | 13.0 | 748.8 x 36.0 | 108 chars / 1 lines |
| TextBox 29 | `medium` | 3 | 13.0 | 108.0 x 28.8 | 14 chars / 1 lines |
| TextBox 30 | `medium` | 39 | 13.0 | 748.8 x 36.0 | 108 chars / 1 lines |
| TextBox 31 | `medium` | 35 | 10.0 | 648.0 x 21.6 | 122 chars / 1 lines |
| TextBox 32 | `medium` | 1 | 10.0 | 43.2 x 21.6 | 6 chars / 1 lines |

## Slide 4

| Shape | Risk | Chars | Font pt | Box pt | Estimate |
| --- | --- | ---: | ---: | --- | --- |
| TextBox 1 | `medium` | 9 | 12.0 | 864.0 x 21.6 | 136 chars / 1 lines |
| TextBox 2 | `medium` | 22 | 26.0 | 871.2 x 57.6 | 63 chars / 1 lines |
| TextBox 8 | `medium` | 35 | 10.0 | 648.0 x 21.6 | 122 chars / 1 lines |
| TextBox 9 | `medium` | 1 | 10.0 | 43.2 x 21.6 | 6 chars / 1 lines |

## Slide 5

| Shape | Risk | Chars | Font pt | Box pt | Estimate |
| --- | --- | ---: | ---: | --- | --- |
| TextBox 1 | `medium` | 2 | 12.0 | 864.0 x 21.6 | 136 chars / 1 lines |
| TextBox 2 | `medium` | 14 | 26.0 | 871.2 x 57.6 | 63 chars / 1 lines |
| TextBox 4 | `medium` | 7 | 15.0 | 172.8 x 28.8 | 20 chars / 1 lines |
| TextBox 5 | `medium` | 20 | 15.0 | 374.4 x 32.4 | 46 chars / 1 lines |
| TextBox 6 | `medium` | 8 | 12.0 | 374.4 x 28.8 | 58 chars / 1 lines |
| TextBox 7 | `medium` | 4 | 15.0 | 172.8 x 28.8 | 20 chars / 1 lines |
| TextBox 8 | `medium` | 14 | 15.0 | 374.4 x 32.4 | 46 chars / 1 lines |
| TextBox 9 | `medium` | 18 | 12.0 | 374.4 x 28.8 | 58 chars / 1 lines |
| TextBox 10 | `medium` | 4 | 15.0 | 172.8 x 28.8 | 20 chars / 1 lines |
| TextBox 11 | `medium` | 21 | 15.0 | 374.4 x 32.4 | 46 chars / 1 lines |
| TextBox 12 | `medium` | 14 | 12.0 | 374.4 x 28.8 | 58 chars / 1 lines |
| TextBox 16 | `medium` | 35 | 10.0 | 648.0 x 21.6 | 122 chars / 1 lines |
| TextBox 17 | `medium` | 1 | 10.0 | 43.2 x 21.6 | 6 chars / 1 lines |

## Slide 6

| Shape | Risk | Chars | Font pt | Box pt | Estimate |
| --- | --- | ---: | ---: | --- | --- |
| TextBox 1 | `medium` | 10 | 12.0 | 864.0 x 21.6 | 136 chars / 1 lines |
| TextBox 2 | `medium` | 17 | 26.0 | 871.2 x 57.6 | 63 chars / 1 lines |
| TextBox 8 | `medium` | 4 | 13.0 | 244.8 x 28.8 | 34 chars / 1 lines |
| TextBox 10 | `medium` | 35 | 10.0 | 648.0 x 21.6 | 122 chars / 1 lines |
| TextBox 11 | `medium` | 1 | 10.0 | 43.2 x 21.6 | 6 chars / 1 lines |

## Slide 7

| Shape | Risk | Chars | Font pt | Box pt | Estimate |
| --- | --- | ---: | ---: | --- | --- |
| TextBox 1 | `medium` | 4 | 12.0 | 864.0 x 21.6 | 136 chars / 1 lines |
| TextBox 2 | `medium` | 16 | 26.0 | 871.2 x 57.6 | 63 chars / 1 lines |
| TextBox 4 | `medium` | 7 | 15.0 | 403.2 x 28.8 | 50 chars / 1 lines |
| TextBox 5 | `medium` | 4 | 13.0 | 115.2 x 28.8 | 15 chars / 1 lines |
| TextBox 6 | `medium` | 18 | 13.0 | 302.4 x 36.0 | 42 chars / 1 lines |
| TextBox 7 | `medium` | 4 | 13.0 | 115.2 x 28.8 | 15 chars / 1 lines |
| TextBox 8 | `medium` | 25 | 13.0 | 302.4 x 36.0 | 42 chars / 1 lines |
| TextBox 9 | `medium` | 4 | 13.0 | 115.2 x 28.8 | 15 chars / 1 lines |
| TextBox 10 | `medium` | 19 | 13.0 | 302.4 x 36.0 | 42 chars / 1 lines |
| TextBox 11 | `medium` | 46 | 15.0 | 424.8 x 28.8 | 52 chars / 1 lines |
| TextBox 16 | `medium` | 35 | 10.0 | 648.0 x 21.6 | 122 chars / 1 lines |
| TextBox 17 | `medium` | 1 | 10.0 | 43.2 x 21.6 | 6 chars / 1 lines |

## Slide 8

| Shape | Risk | Chars | Font pt | Box pt | Estimate |
| --- | --- | ---: | ---: | --- | --- |
| TextBox 1 | `medium` | 2 | 12.0 | 864.0 x 21.6 | 136 chars / 1 lines |
| TextBox 2 | `medium` | 9 | 26.0 | 871.2 x 57.6 | 63 chars / 1 lines |
| TextBox 10 | `medium` | 35 | 10.0 | 648.0 x 21.6 | 122 chars / 1 lines |
| TextBox 11 | `medium` | 1 | 10.0 | 43.2 x 21.6 | 6 chars / 1 lines |
