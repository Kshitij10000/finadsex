export const ConnectionStatus = ({ status }) => {
  const getStatusColor = () => {
    switch (status) {
      case 'Connected':
        return 'var(--status-connected)';
      case 'Connecting...':
        return 'var(--status-connecting)';
      case 'Error':
        return 'var(--status-error)';
      default:
        return 'var(--status-disconnected)';
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'Connected':
        return 'Active';
      case 'Connecting...':
        return 'Connecting';
      case 'Error':
        return 'Error';
      default:
        return 'Offline';
    }
  };

  return (
    <div className="connection-status-minimal">
      <span
        className="status-dot-small"
        style={{ backgroundColor: getStatusColor() }}
      />
      <span className="status-text" style={{ color: getStatusColor() }}>
        {getStatusText()}
      </span>
    </div>
  );
};