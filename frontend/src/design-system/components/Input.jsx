import React from 'react';
import './Input.css';

const Input = ({
  type = 'text',
  size = 'md',
  error = false,
  disabled = false,
  icon = null,
  className = '',
  ...props
}) => {
  const classNames = [
    'ds-input',
    `ds-input--${size}`,
    error && 'ds-input--error',
    disabled && 'ds-input--disabled',
    icon && 'ds-input--with-icon',
    className
  ].filter(Boolean).join(' ');

  return (
    <div className="ds-input-wrapper">
      {icon && (
        <span className="ds-input__icon">{icon}</span>
      )}
      <input
        type={type}
        className={classNames}
        disabled={disabled}
        {...props}
      />
    </div>
  );
};

export default Input;