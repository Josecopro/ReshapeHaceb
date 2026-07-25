import type { ReactNode } from 'react';

interface ModalField {
  label: string;
  value: string | ReactNode;
}

interface FloatingModalProps {
  title: string;
  fields: ModalField[];
  onClose: () => void;
}

const FloatingModal = ({ title, fields, onClose }: FloatingModalProps) => (
  <div className="modal-overlay" onClick={onClose}>
    <div className="modal-content" onClick={e => e.stopPropagation()}>
      <div className="modal-header">
        <div className="modal-title">{title}</div>
        <button className="modal-close" onClick={onClose}>×</button>
      </div>
      {fields.map((field, i) => (
        <div className="modal-field" key={i} style={{ animationDelay: `${i * 0.08}s` }}>
          <div className="modal-field-label">{field.label}</div>
          <div className="modal-field-value">{field.value}</div>
        </div>
      ))}
    </div>
  </div>
);

export default FloatingModal;
