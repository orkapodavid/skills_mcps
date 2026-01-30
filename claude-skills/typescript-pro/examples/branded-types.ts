/**
 * Branded Types Example
 * 
 * Branded types (also known as nominal types or opaque types) allow you to create
 * distinct types that are structurally compatible with their base type but are
 * treated as different types by the TypeScript compiler. This is useful for
 * preventing accidental mixing of different types of values (e.g. UserID vs PostID).
 */

declare const __brand: unique symbol;

/**
 * Helper type to create a branded type.
 * T: The base type (e.g., number, string)
 * B: The unique brand string
 */
export type Brand<T, B> = T & { [__brand]: B };

/**
 * Domain-specific branded types
 */
export type UserId = Brand<string, "UserId">;
export type PostId = Brand<string, "PostId">;
export type EmailAddress = Brand<string, "EmailAddress">;
export type USD = Brand<number, "USD">;
export type EUR = Brand<number, "EUR">;

// --- Usage Examples ---

/**
 * Type guard validation function for EmailAddress
 */
export function isEmailAddress(value: string): value is EmailAddress {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
}

/**
 * Factory function for UserId
 */
export function createUserId(id: string): UserId {
    // In a real app, you might validate UUID format here
    return id as UserId;
}

/**
 * Example function that requires specific branded types
 */
export function sendEmail(userId: UserId, email: EmailAddress): void {
    console.log(`Sending email to user ${userId} at ${email}`);
}

/**
 * Currency conversion example
 */
export function convertUsdToEur(amount: USD, rate: number): EUR {
    return (amount * rate) as EUR;
}

// --- Compile-time Safety Checks ---

function main() {
    const userId = createUserId("user_123");
    const specificPostId = "post_456" as PostId;
    const emailStr = "test@example.com";

    // Error: Argument of type 'string' is not assignable to parameter of type 'EmailAddress'.
    // sendEmail(userId, emailStr); 

    if (isEmailAddress(emailStr)) {
        // Valid: emailStr is narrowed to EmailAddress here
        sendEmail(userId, emailStr);
    }

    // Error: Argument of type 'PostId' is not assignable to parameter of type 'UserId'.
    // sendEmail(specificPostId, emailStr as EmailAddress);
}
