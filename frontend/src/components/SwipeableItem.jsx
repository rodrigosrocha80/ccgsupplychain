import { useSwipeable } from 'react-swipeable';

const SwipeableItem = ({ children, onSwipeLeft, onSwipeRight }) => {
  const handlers = useSwipeable({
    onSwipedLeft: onSwipeLeft,
    onSwipedRight: onSwipeRight,
    trackMouse: true,
    delta: 50
  });

  return (
    <div {...handlers} className="touch-pan-y">
      {children}
    </div>
  );
};

export default SwipeableItem;