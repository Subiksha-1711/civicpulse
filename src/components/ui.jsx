import { X } from 'lucide-react';

export function Button({ variant = 'primary', size, className = '', children, ...props }) {
  const variantClass = { primary: 'btn-primary', secondary: 'btn-secondary', outline: 'btn-outline', danger: 'btn-danger' }[variant] || 'btn-primary';
  const sizeClass = size === 'sm' ? 'btn-sm' : '';
  return (
    <button className={`btn ${variantClass} ${sizeClass} ${className}`} {...props}>
      {children}
    </button>
  );
}

export function Field({ label, required, error, children }) {
  return (
    <div className="field">
      {label && (
        <label>
          {label} {required && <span className="required">*</span>}
        </label>
      )}
      {children}
      {error && <div className="field-error">{error}</div>}
    </div>
  );
}

export function LoadingSpinner({ center }) {
  if (center) return <div className="spinner-center"><div className="spinner" /></div>;
  return <div className="spinner" />;
}

export function EmptyState({ icon: Icon, title, message }) {
  return (
    <div className="empty-state">
      {Icon && <Icon size={40} />}
      <h3 style={{ margin: '0 0 6px' }}>{title}</h3>
      <p style={{ margin: 0 }}>{message}</p>
    </div>
  );
}

export function Modal({ title, onClose, children }) {
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="card modal-box" onClick={(e) => e.stopPropagation()}>
        <div className="modal-head">
          <h3 style={{ margin: 0 }}>{title}</h3>
          <button className="modal-close" onClick={onClose} aria-label="Close">
            <X size={20} />
          </button>
        </div>
        {children}
      </div>
    </div>
  );
}

export function Switch({ on, onToggle, label }) {
  return (
    <button
      className={`switch ${on ? 'on' : ''}`}
      onClick={onToggle}
      role="switch"
      aria-checked={on}
      aria-label={label}
      type="button"
    >
      <span className="knob" />
    </button>
  );
}
