export const getDeviceType = () => {
  const userAgent = navigator.userAgent || navigator.vendor || window.opera;
  
  // iOS detection
  if (/iPad|iPhone|iPod/.test(userAgent) && !window.MSStream) {
    return 'ios';
  }
  
  // Mac detection
  if (navigator.platform.toUpperCase().indexOf('MAC') >= 0) {
    return 'mac';
  }
  
  // Android detection
  if (/android/i.test(userAgent)) {
    return 'android';
  }
  
  // Windows Phone detection
  if (/windows phone/i.test(userAgent)) {
    return 'windows-phone';
  }
  
  // Default to PC for everything else
  return 'pc';
};

export const getAvailablePaymentMethods = () => {
  const deviceType = getDeviceType();
  
  // Common payment methods for all devices
  const commonMethods = [
    {
      id: 'bank-transfer',
      name: 'Przelew bankowy',
      description: 'Tradycyjny przelew bankowy',
      icon: '🏦',
      available: true
    },
    {
      id: 'blik',
      name: 'BLIK',
      description: 'Szybka płatność kodem BLIK',
      icon: '📱',
      available: true
    },
    {
      id: 'card',
      name: 'Karta płatnicza',
      description: 'Visa, Mastercard, Maestro',
      icon: '💳',
      available: true
    }
  ];
  
  // Device-specific payment methods
  const deviceSpecificMethods = [];
  
  if (deviceType === 'ios' || deviceType === 'mac') {
    deviceSpecificMethods.push({
      id: 'apple-pay',
      name: 'Apple Pay',
      description: 'Zapłać używając Apple Pay',
      icon: '🍎',
      available: true,
      primary: true
    });
  } else {
    // Android, PC, and others get Google Pay
    deviceSpecificMethods.push({
      id: 'google-pay',
      name: 'Google Pay',
      description: 'Zapłać używając Google Pay',
      icon: '🇬',
      available: true,
      primary: true
    });
  }
  
  // Return device-specific methods first, then common methods
  return [...deviceSpecificMethods, ...commonMethods];
};

export const isAppleDevice = () => {
  const deviceType = getDeviceType();
  return deviceType === 'ios' || deviceType === 'mac';
};

export const isMobileDevice = () => {
  const deviceType = getDeviceType();
  return ['ios', 'android', 'windows-phone'].includes(deviceType);
};