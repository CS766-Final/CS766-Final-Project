Sudocode for this idea

```c
void highlight_recovery(TYPE rgb[3])
{
  // find the indices of the max, median, and min RGB values
  integer max_index(0)      // contains index of the V channel
  integer median_index(0)   // contains index of the channel H will be estimated from
  integer min_index(0)      // contains index of the channel S will be estimated from

  for (index = 1 through 2)
  {
    if (max < rgb[index]) max_index = [index]
    if (min > rgb[index]) min_index = [index]
  }
  while (median_index is equal to max_index or median_index is equal to min_index)
    median_index = median_index + 1

  // find the clipped pixel values
  TYPE clipped[3]
  for (index = 0 through 2)
  {
    if (rgb[index] > MAX)
      clipped[index] = MAX
    else
      clipped[index] = rgb[index]
  }

  // get H
  float H
  if (rgb[max_index] is not equal to rgb[min_index])
    H = float((rgb[median_index] - rgb[min_index]) / (rgb[max_index] - rgb[min_index]))
  else if (clipped[max_index] is not equal to clipped[min_index])
    H = float((clipped[median_index] - clipped[min_index]) / (clipped[max_index] - clipped[min_index]))
  else
    H = 0

  // get S
  float S
  if (clipped[max_index] is not equal to 0)
    S = 1.f - float(clipped[min_index] / clipped[max_index])

  // convert HSV values back to RGB
  rgb[median_index] = rgb[max_index] * (1.f - S + S * H)
  rgb[min_index]    = rgb[max_index] * (1.f - S)
}
```

city_comp.png conf
neutral: 1.2282886 1 1.6131868
color matrix: 1.4868945 -0.6438222 -0.0699355 -0.261274 1.0494869 0.1399011 -0.1775877 0.313115 0.4792254

We do all of our calculations in the camera color space and then convert to srgb color space before saving the image.
