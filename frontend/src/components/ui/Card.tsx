import { HTMLAttributes, forwardRef } from 'react'
import { clsx } from 'clsx'

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'bordered' | 'elevated'
}

const Card = forwardRef<HTMLDivElement, CardProps>(
  ({ className, variant = 'default', children, ...props }, ref) => {
    const variants = {
      default: 'bg-white rounded-lg shadow-sm border border-gray-200',
      bordered: 'bg-white rounded-lg border-2 border-gray-300',
      elevated: 'bg-white rounded-lg shadow-lg border border-gray-100'
    }
    
    return (
      <div
        ref={ref}
        className={clsx(variants[variant], className)}
        {...props}
      >
        {children}
      </div>
    )
  }
)

Card.displayName = 'Card'

export default Card 