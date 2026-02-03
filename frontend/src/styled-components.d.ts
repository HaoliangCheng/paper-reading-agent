import 'styled-components';
import { ThemeType } from './theme/Theme';

declare module 'styled-components' {
  export interface DefaultTheme extends ThemeType {}
}
