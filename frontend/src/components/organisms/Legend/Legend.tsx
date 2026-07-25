import './Legend.scss';

interface LegendItem {
  label: string;
  color: string;
  dashed?: boolean;
  pulse?: boolean;
}

interface LegendProps {
  items: LegendItem[];
}

const Legend = ({ items }: LegendProps) => (
  <div className="legend">
    {items.map((item, i) => (
      <div className="legend__item" key={i} style={{ animationDelay: `${i * 0.1}s` }}>
        <div
          className={`legend__swatch${item.dashed ? ' legend__swatch--dashed' : ''}${item.pulse ? ' legend__swatch--pulse' : ''}`}
          style={item.dashed ? { borderColor: item.color } : { backgroundColor: item.color }}
        />
        <span className="legend__text">{item.label}</span>
      </div>
    ))}
  </div>
);

export default Legend;
