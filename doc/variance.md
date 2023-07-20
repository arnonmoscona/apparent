# Variance computation

Most of the contents here is a copy from [wikipedia.com](https://en.wikipedia.org/wiki/Algorithms_for_calculating_variance#Computing_shifted_data) - all right thereof reserved.

Here the algorithm chosen was the shofted value algorithm as it is the more time efficient
and this is the ovveriding concern in the context of monitoring: minimizing time
and space overhead of any measurement.

From wikipedia:

> The variance is invariant with respect to changes in a location parameter, 
> a property which can be used to avoid the catastrophic cancellation in this formula.
> 
> ![](variance.svg)
> with ![](K.svg) any constant, which leads to the new formula
> 
> ![](variance_calc.svg)
> 
> the closer ![](K.svg) is to the mean value the more accurate the result will be, 
> but just choosing a value inside the samples range will guarantee the desired stability. 
> If the values ![](diffs.svg) are small then there are no problems with the sum of 
> its squares, on the contrary, if they are large it necessarily means that the 
> variance is large as well. In any case the second term in the formula is always 
> smaller than the first one therefore no cancellation may occur.